"""Exercise wire records independently of a native client or model SDK."""

import http.client
import json
import socket
import time

import pytest

from tests.support.offline_provider import Step, offline_provider

pytestmark = pytest.mark.unit


def request(provider, path, value, *, timeout=2, headers=None):
    connection = http.client.HTTPConnection("127.0.0.1", provider.server_port, timeout=timeout)
    try:
        connection.request(
            "POST", path, json.dumps(value), headers or {"Content-Type": "application/json"}
        )
        response = connection.getresponse()
        return response.status, response.getheader("Content-Type"), response.read()
    finally:
        connection.close()


def payload(protocol, stream=False):
    return {
        "model": "fixture-model",
        "stream": stream,
        "input" if protocol == "responses" else "messages": [
            {"role": "user", "content": "SYNTHETIC_CONTEXT_7319"}
        ],
    }


def parse_sse(data):
    return [
        json.loads(line[6:])
        for line in data.decode().splitlines()
        if line.startswith("data: ") and line != "data: [DONE]"
    ]


@pytest.mark.parametrize(
    "protocol,path",
    [
        ("chat", "/v1/chat/completions"),
        ("responses", "/v1/responses"),
        ("messages", "/v1/messages?beta=true"),
    ],
)
@pytest.mark.parametrize("stream", [False, True])
def test_fixed_text_request_recording_and_terminal_events(protocol, path, stream):
    with offline_provider((Step(text="FIXED 世界"),)) as provider:
        status, content_type, body = request(provider, path, payload(protocol, stream))
        assert status == 200
        assert "FIXED 世界" in body.decode()
        assert provider.requests[0][0] == path
        assert "SYNTHETIC_CONTEXT_7319" in json.dumps(provider.requests[0][1])
        if stream:
            assert content_type == "text/event-stream"
            events = parse_sse(body)
            if protocol == "chat":
                assert events[-1]["choices"][0]["finish_reason"] == "stop"
                assert body.endswith(b"data: [DONE]\n\n")
            elif protocol == "responses":
                assert events[-1]["type"] == "response.completed"
                assert events[-1]["response"]["status"] == "completed"
                assert [e["sequence_number"] for e in events] == list(range(len(events)))
            else:
                assert events[-1]["type"] == "message_stop"
                assert b"event: message_stop" in body
        else:
            assert content_type == "application/json"
            value = json.loads(body)
            assert value["id"].endswith("1")
        provider.assert_clean()


@pytest.mark.parametrize(
    "protocol,path",
    [("chat", "/chat/completions"), ("responses", "/responses"), ("messages", "/messages")],
)
@pytest.mark.parametrize("stream", [False, True])
def test_tool_call_followed_by_linked_result_and_text(protocol, path, stream):
    with offline_provider((Step(kind="tool"), Step(text="TOOL_RESULT_RECORDED"))) as provider:
        _, _, body = request(provider, path, payload(protocol, stream))
        values = parse_sse(body) if stream else [json.loads(body)]
        serialized = json.dumps(values)
        assert "call_1" in serialized and "synthetic.txt" in serialized
        if protocol == "chat":
            tool_result = {
                "role": "tool",
                "tool_call_id": "call_1",
                "content": "SYNTHETIC_TOOL_RESULT",
            }
            finish = values[-1]["choices"][0]["finish_reason"]
            assert finish == "tool_calls"
        elif protocol == "responses":
            tool_result = {
                "type": "function_call_output",
                "call_id": "call_1",
                "output": "SYNTHETIC_TOOL_RESULT",
            }
            if stream:
                assert any(e["type"] == "response.function_call_arguments.done" for e in values)
            else:
                assert values[0]["output"][0]["type"] == "function_call"
        else:
            tool_result = {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "call_1",
                        "content": "SYNTHETIC_TOOL_RESULT",
                    }
                ],
            }
            if stream:
                assert values[-2]["delta"]["stop_reason"] == "tool_use"
            else:
                assert values[0]["stop_reason"] == "tool_use"
        continuation = payload(protocol, stream)
        assistant_call = {
            "chat": {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_1",
                        "type": "function",
                        "function": {"name": "read", "arguments": '{"path":"synthetic.txt"}'},
                    }
                ],
            },
            "responses": {
                "type": "function_call",
                "call_id": "call_1",
                "name": "read",
                "arguments": '{"path":"synthetic.txt"}',
            },
            "messages": {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "id": "call_1",
                        "name": "read",
                        "input": {"path": "synthetic.txt"},
                    }
                ],
            },
        }[protocol]
        continuation["input" if protocol == "responses" else "messages"].extend(
            [
                assistant_call,
                tool_result,
            ]
        )
        status, _, reply = request(provider, path, continuation)
        assert status == 200 and b"TOOL_RESULT_RECORDED" in reply
        assert "call_1" in json.dumps(provider.requests[-1])
        assert "SYNTHETIC_TOOL_RESULT" in json.dumps(provider.requests[-1])
        provider.assert_clean()


@pytest.mark.parametrize(
    "path", ["/v1/unknown", "/other/messages", "/v1/messages?secret=bad", "/v1/responses?beta=true"]
)
def test_unknown_paths_and_queries_are_rejected(provider, path):
    status, _, _ = request(provider, path, payload("chat"))
    assert status == 404 and provider.requests == []
    with pytest.raises(AssertionError, match="unknown_endpoint"):
        provider.assert_clean()


@pytest.mark.parametrize(
    "value",
    [
        [],
        {},
        {"model": "x", "messages": []},
        {"model": "x", "messages": ["bad"]},
        {"model": "x", "messages": [{}], "stream": "yes"},
    ],
)
def test_invalid_request_shapes(provider, value):
    status, _, _ = request(provider, "/v1/messages", value)
    assert status == 400 and provider.requests == []


@pytest.mark.parametrize(
    "body", [b'{"model":"x","model":"y","messages":[]}', b'{"model":NaN}', b"\xff", b"{broken"]
)
def test_malformed_json_never_records_content(provider, body):
    connection = http.client.HTTPConnection("127.0.0.1", provider.server_port, timeout=2)
    try:
        connection.request("POST", "/messages", body, {"Content-Type": "application/json"})
        assert connection.getresponse().status == 400
    finally:
        connection.close()
    assert not provider.requests


def test_body_and_request_budgets_and_dummy_credentials():
    with offline_provider(max_body=20) as provider:
        assert request(provider, "/responses", payload("responses"))[0] == 413
    with offline_provider(max_requests=1) as provider:
        assert request(provider, "/responses", payload("responses"))[0] == 200
        assert request(provider, "/responses", payload("responses"))[0] == 429
    with offline_provider() as provider:
        assert (
            request(
                provider,
                "/responses",
                payload("responses"),
                headers={"Content-Type": "application/json", "Authorization": "Bearer local-dummy"},
            )[0]
            == 200
        )
        assert (
            request(
                provider,
                "/responses",
                payload("responses"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer must-not-be-used",
                },
            )[0]
            == 401
        )
        assert (
            request(
                provider, "/responses", payload("responses"), headers={"Content-Type": "text/plain"}
            )[0]
            == 400
        )


@pytest.mark.parametrize(
    "protocol,path",
    [("chat", "/chat/completions"), ("responses", "/responses"), ("messages", "/messages")],
)
def test_provider_error_and_malformed_events(protocol, path):
    with offline_provider((Step(kind="error", status=503), Step(kind="malformed"))) as provider:
        assert request(provider, path, payload(protocol))[0] == 503
        status, _, body = request(provider, path, payload(protocol, True))
        assert status == 200
        with pytest.raises(json.JSONDecodeError):
            parse_sse(body)


def test_timeout_cleanup_releases_handlers_and_listener():
    start = time.monotonic()
    with offline_provider((Step(kind="timeout"),)) as provider:
        port = provider.server_port
        with pytest.raises(socket.timeout):
            request(provider, "/responses", payload("responses"), timeout=0.05)
    assert time.monotonic() - start < 5
    with pytest.raises(OSError):
        socket.create_connection(("127.0.0.1", port), timeout=0.1)


def test_health_models_and_unknown_get(provider):
    for path, status in [("/health", 200), ("/v1/models", 200), ("/unknown", 404)]:
        connection = http.client.HTTPConnection("127.0.0.1", provider.server_port, timeout=2)
        try:
            connection.request("GET", path)
            response = connection.getresponse()
            assert response.status == status
            response.read()
        finally:
            connection.close()
