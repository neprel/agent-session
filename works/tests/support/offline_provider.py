"""Deterministic loopback wire stub, with no model or outbound HTTP client.

Adapted from xhluca/session-migrate tests/offline_provider.py, revision
fefb719088dc0157b16f071065daa30434a0b980, copyright (c) 2026 xhluca, MIT.
See LICENSE.session-migrate. Changes: bounded strict requests, query handling,
scripted tools/failures, unique deterministic IDs, no Gemini, bounded cleanup.
"""

import json
import threading
from collections import deque
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Literal
from urllib.parse import parse_qs, urlsplit

PATHS = {
    "/chat/completions": "chat",
    "/v1/chat/completions": "chat",
    "/responses": "responses",
    "/v1/responses": "responses",
    "/messages": "messages",
    "/v1/messages": "messages",
}


@dataclass(frozen=True)
class Step:
    kind: Literal["text", "tool", "error", "timeout", "malformed"] = "text"
    text: str = "SYNTHETIC_FIXED_REPLY"
    tool_name: str = "read"
    arguments: str = '{"path":"synthetic.txt"}'
    status: int = 503


class OfflineProvider(ThreadingHTTPServer):
    daemon_threads = False
    block_on_close = True

    def __init__(self, steps: tuple[Step, ...], max_body: int, max_requests: int):
        super().__init__(("127.0.0.1", 0), Handler)
        self.steps = deque(steps)
        self.requests: list[tuple[str, dict]] = []
        self.rejections: list[str] = []
        self.max_body = max_body
        self.max_requests = max_requests
        self.lock = threading.Lock()
        self.release = threading.Event()

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.server_port}"

    def assert_clean(self) -> None:
        assert not self.rejections, f"unexpected provider requests: {self.rejections}"


def strict_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate key")
        value[key] = item
    return value


def invalid_constant(value):
    raise ValueError("non-finite JSON")


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def setup(self):
        super().setup()
        self.connection.settimeout(1)

    def log_message(self, format, *args):
        pass

    def reject(self, status: int, code: str):
        self.server.rejections.append(code)
        self.close_connection = True
        self.body(
            json.dumps({"error": {"type": code, "message": "synthetic request rejected"}}).encode(),
            "application/json",
            status,
        )

    def do_GET(self):  # noqa: N802
        if self.path == "/health":
            self.json({"status": "ok"})
        elif self.path in {"/models", "/v1/models"}:
            self.json(
                {
                    "object": "list",
                    "data": [{"id": "fixture-model", "object": "model", "owned_by": "synthetic"}],
                }
            )
        else:
            self.reject(404, "unknown_endpoint")

    def do_POST(self):  # noqa: N802
        parsed = urlsplit(self.path)
        protocol = PATHS.get(parsed.path)
        query = parse_qs(parsed.query, keep_blank_values=True)
        if (
            not protocol
            or parsed.fragment
            or (parsed.query and not (protocol == "messages" and query == {"beta": ["true"]}))
        ):
            self.reject(404, "unknown_endpoint")
            return
        if (
            self.headers.get("Transfer-Encoding")
            or len(self.headers.get_all("Content-Length", [])) != 1
            or self.headers.get_content_type() != "application/json"
        ):
            self.reject(400, "invalid_framing")
            return
        authorization = self.headers.get("Authorization")
        key = self.headers.get("x-api-key")
        if (authorization and authorization != "Bearer local-dummy") or (
            key and key != "local-dummy"
        ):
            self.reject(401, "nonlocal_credential")
            return
        try:
            length = int(self.headers["Content-Length"])
            if length <= 0 or length > self.server.max_body:
                self.reject(413, "body_limit")
                return
            data = self.rfile.read(length)
            if len(data) != length:
                raise ValueError("incomplete body")
            value = json.loads(
                data, object_pairs_hook=strict_object, parse_constant=invalid_constant
            )
            if (
                not isinstance(value, dict)
                or not isinstance(value.get("model"), str)
                or not value["model"]
            ):
                raise ValueError("invalid model")
            if "stream" in value and not isinstance(value["stream"], bool):
                raise ValueError("invalid stream")
            content = value.get("input" if protocol == "responses" else "messages")
            if protocol == "responses" and isinstance(content, str):
                if not content:
                    raise ValueError("empty input")
            elif (
                not isinstance(content, list)
                or not content
                or any(not isinstance(m, dict) for m in content)
            ):
                raise ValueError("invalid conversation")
            if isinstance(content, list):
                for message in content:
                    if protocol == "responses" and message.get("type") in {
                        "function_call",
                        "function_call_output",
                    }:
                        if not message.get("call_id"):
                            raise ValueError("missing tool linkage")
                    elif message.get("role") not in {
                        "user",
                        "assistant",
                        "system",
                        "developer",
                        "tool",
                    } or not isinstance(message.get("content"), str | list | type(None)):
                        raise ValueError("invalid message")
        except (TimeoutError, TypeError, ValueError, UnicodeDecodeError):
            self.reject(400, "invalid_request")
            return
        with self.server.lock:
            if len(self.server.requests) >= self.server.max_requests:
                self.reject(429, "request_limit")
                return
            self.server.requests.append((self.path, value))
            sequence = len(self.server.requests)
            step = self.server.steps.popleft() if self.server.steps else Step()
        if step.kind == "error":
            self.json(
                {
                    "type": "error",
                    "error": {"type": "overloaded_error", "message": "synthetic provider error"},
                },
                step.status,
            )
        elif step.kind == "timeout":
            self.server.release.wait(timeout=2)
            self.json({"error": {"type": "synthetic_timeout"}}, 504)
        elif step.kind == "malformed":
            self.body(b"data: {not-json}\n\n", "text/event-stream")
        else:
            getattr(self, "_" + protocol)(value, step, sequence)

    def _chat(self, request: dict, step: Step, sequence: int):
        call = {
            "id": f"call_{sequence}",
            "type": "function",
            "function": {"name": step.tool_name, "arguments": step.arguments},
        }
        message = (
            {"role": "assistant", "content": step.text}
            if step.kind == "text"
            else {"role": "assistant", "content": None, "tool_calls": [call]}
        )
        finish = "stop" if step.kind == "text" else "tool_calls"
        base = {"id": f"chatcmpl_{sequence}", "created": 1788220000, "model": request["model"]}
        usage = {"prompt_tokens": 10, "completion_tokens": 3, "total_tokens": 13}
        if not request.get("stream"):
            self.json(
                {
                    **base,
                    "object": "chat.completion",
                    "choices": [{"index": 0, "message": message, "finish_reason": finish}],
                    "usage": usage,
                }
            )
            return
        delta = (
            {"role": "assistant", "content": step.text}
            if step.kind == "text"
            else {"role": "assistant", "tool_calls": [{"index": 0, **call}]}
        )
        events = [
            {
                **base,
                "object": "chat.completion.chunk",
                "choices": [{"index": 0, "delta": delta, "finish_reason": None}],
            },
            {
                **base,
                "object": "chat.completion.chunk",
                "choices": [{"index": 0, "delta": {}, "finish_reason": finish}],
                "usage": usage,
            },
        ]
        self.sse(events, done=True)

    def _responses(self, request: dict, step: Step, sequence: int):
        item = (
            {
                "id": f"msg_{sequence}",
                "type": "message",
                "status": "completed",
                "role": "assistant",
                "content": [{"type": "output_text", "text": step.text, "annotations": []}],
            }
            if step.kind == "text"
            else {
                "id": f"fc_{sequence}",
                "type": "function_call",
                "status": "completed",
                "call_id": f"call_{sequence}",
                "name": step.tool_name,
                "arguments": step.arguments,
            }
        )
        response = {
            "id": f"resp_{sequence}",
            "object": "response",
            "created_at": 1788220000,
            "status": "completed",
            "error": None,
            "incomplete_details": None,
            "model": request["model"],
            "output": [item],
            "store": False,
            "usage": {
                "input_tokens": 10,
                "output_tokens": 3,
                "total_tokens": 13,
                "input_tokens_details": {"cached_tokens": 0},
                "output_tokens_details": {"reasoning_tokens": 0},
            },
        }
        if not request.get("stream"):
            self.json(response)
            return
        events = [
            {
                "type": "response.created",
                "response": {**response, "status": "in_progress", "output": []},
            },
            {
                "type": "response.output_item.added",
                "output_index": 0,
                "item": {
                    **item,
                    "status": "in_progress",
                    **({"content": []} if step.kind == "text" else {"arguments": ""}),
                },
            },
        ]
        if step.kind == "text":
            events.extend(
                [
                    {
                        "type": "response.content_part.added",
                        "item_id": item["id"],
                        "output_index": 0,
                        "content_index": 0,
                        "part": {"type": "output_text", "text": "", "annotations": []},
                    },
                    {
                        "type": "response.output_text.delta",
                        "item_id": item["id"],
                        "output_index": 0,
                        "content_index": 0,
                        "delta": step.text,
                    },
                    {
                        "type": "response.output_text.done",
                        "item_id": item["id"],
                        "output_index": 0,
                        "content_index": 0,
                        "text": step.text,
                    },
                    {
                        "type": "response.content_part.done",
                        "item_id": item["id"],
                        "output_index": 0,
                        "content_index": 0,
                        "part": item["content"][0],
                    },
                ]
            )
        else:
            events.extend(
                [
                    {
                        "type": "response.function_call_arguments.delta",
                        "item_id": item["id"],
                        "output_index": 0,
                        "delta": step.arguments,
                    },
                    {
                        "type": "response.function_call_arguments.done",
                        "item_id": item["id"],
                        "output_index": 0,
                        "arguments": step.arguments,
                    },
                ]
            )
        events.extend(
            [
                {"type": "response.output_item.done", "output_index": 0, "item": item},
                {"type": "response.completed", "response": response},
            ]
        )
        self.sse(events)

    def _messages(self, request: dict, step: Step, sequence: int):
        block = (
            {"type": "text", "text": step.text}
            if step.kind == "text"
            else {
                "type": "tool_use",
                "id": f"call_{sequence}",
                "name": step.tool_name,
                "input": json.loads(step.arguments),
            }
        )
        stop = "end_turn" if step.kind == "text" else "tool_use"
        message = {
            "id": f"msg_{sequence}",
            "type": "message",
            "role": "assistant",
            "model": request["model"],
            "content": [block],
            "stop_reason": stop,
            "stop_sequence": None,
            "usage": {"input_tokens": 10, "output_tokens": 3},
        }
        if not request.get("stream"):
            self.json(message)
            return
        delta = (
            {"type": "text_delta", "text": step.text}
            if step.kind == "text"
            else {"type": "input_json_delta", "partial_json": step.arguments}
        )
        initial = {"type": "text", "text": ""} if step.kind == "text" else {**block, "input": {}}
        self.sse(
            [
                {
                    "type": "message_start",
                    "message": {**message, "content": [], "stop_reason": None},
                },
                {"type": "content_block_start", "index": 0, "content_block": initial},
                {"type": "content_block_delta", "index": 0, "delta": delta},
                {"type": "content_block_stop", "index": 0},
                {
                    "type": "message_delta",
                    "delta": {"stop_reason": stop, "stop_sequence": None},
                    "usage": {"output_tokens": 3},
                },
                {"type": "message_stop"},
            ],
            named=True,
        )

    def json(self, value, status=200):
        self.body(
            json.dumps(value, ensure_ascii=False, allow_nan=False).encode(),
            "application/json",
            status,
        )

    def sse(self, events, *, named=False, done=False):
        parts = []
        for index, event in enumerate(events):
            if event.get("type", "").startswith("response."):
                event = {**event, "sequence_number": index}
            prefix = f"event: {event['type']}\n" if named else ""
            parts.append(f"{prefix}data: {json.dumps(event, ensure_ascii=False)}\n\n")
        if done:
            parts.append("data: [DONE]\n\n")
        self.body("".join(parts).encode(), "text/event-stream")

    def body(self, body: bytes, content_type: str, status=200):
        self.close_connection = True
        try:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)
        except (TimeoutError, BrokenPipeError, ConnectionResetError):
            pass


@contextmanager
def offline_provider(
    steps: tuple[Step, ...] = (), *, max_body=4 * 1024**2, max_requests=32
) -> Iterator[OfflineProvider]:
    provider = OfflineProvider(steps, max_body, max_requests)
    thread = threading.Thread(target=provider.serve_forever, kwargs={"poll_interval": 0.01})
    thread.start()
    try:
        yield provider
    finally:
        provider.release.set()
        provider.shutdown()
        provider.server_close()
        thread.join(timeout=5)
        assert not thread.is_alive(), "provider did not terminate"
