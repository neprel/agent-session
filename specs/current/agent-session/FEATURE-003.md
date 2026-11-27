# Delivery and adapter architecture

## R1 - Adapter contract

Use a small explicit registry in harnesses/__init__.py. Define one common typed Harness protocol in harnesses/base.py. Each harness MUST implement this interface in its own package. Define typed requests, results and capability declarations in the common contract. The following method names and responsibilities are required; define concrete argument and result types in AS-002.

| Method | Responsibility |
|---|---|
| discover | Discover the native session ID, launch target and live endpoints. Parse native hook input if applicable. |
| probe | Check native session identity, reachability and activity without launching a harness or invoking inference. |
| launch | Return native executable arguments, working directory and environment for a new or saved session. Do not launch in this method. |
| send | Submit a message and return a defined delivery result. |
| read_history | Read native history into the common portable event model. Return validated cursor, provenance and loss information. |
| write_history | Materialize portable events as a new native session. Return verified session ID, projection boundary and loss information. |
| configure | Plan and install native integration resources. Preserve unrelated user configuration. Support dry-run. |
| configure_options | Declare additional harness-specific CLI options where necessary. Return no options if none are needed. |

Declare supported capabilities and tested version ranges. Implement each interface member or return the defined unsupported result. Do not guess missing capabilities. Keep native paths, environment variable discovery, API requests, hook payload parsing, native history formats and lifecycle resources inside the harness package. Keep common storage and synchronization direction in history.py, not in individual harnesses. Keep common delivery policy in delivery.py. Keep tmux in tmux.py as a shared fallback, not a harness. Do not use argparse or CLI exit codes in harness implementations. Use safe command arrays, bounded timeouts and strict input validation.

Use package-relative resources (importlib.resources). Build hook configuration fragments as Python dictionaries in the owning adapter. Put TypeScript extensions/plugins and other executable native resources in their own harness package. Do not ship JSON hook or settings templates. Do not use a central harness template directory. A harness may split private native conversion or transport code into additional modules inside its package, but adapter.py implements the complete common interface.

Add a fake harness in tests. Prove that a new harness needs only its implementation package and registry entry for common operations. Harness-specific CLI options, if necessary, are registered through a harness-provided option declaration, not a conditional block in cli.py. Validate the public CLI behavior against FEATURE-001. No changes to watcher, timer, common history storage, delivery routing or CLI dispatch are permitted for a new harness.

## R2 - Message

Read one positional text argument or all stdin; reject empty input or ambiguous inputs. Preserve multiline text and Unicode. Resolve current harness only. Check ownership and liveness. Prefer native transport. Use tmux only after definite non-delivery and verified safe fallback. Do not fall back after uncertain acceptance. Return accepted, unavailable, unsupported, deferred or uncertain internally, and map to common exit codes (deferred: 3 with reason). No infinite retries or automatic resume. Do not interpret text as shell commands. For background triggers use the shared delivery function, not a new CLI process. Serialize deliveries to the same runtime as needed. Do not bypass permission prompts. If a transport cannot prove safe queuing or safe idle state, defer or fail rather than inject terminal input.

### Sender and reply routing

Accept optional `--from PATH` on the message command only. Resolve PATH with the same rules as `--target`, relative to the caller's working directory. Require a valid sender registration; do not require a live sender. Reject invalid sender targets before delivery. Use the absolute resolved registration file path as `from`. Send a JSON object with exactly two fields, `from` and `message`. Preserve the original message text in the `message` field, including Unicode and line breaks. Example:

```json
{
  "from": "/workspace/agents/platform-backend-developer/1/.session/agent.json",
  "message": "TASK-042 is ready for review."
}
```

If `--from` is absent, send the original text without an envelope. The recipient can use the `from` value as `--target` to reply. Treat `from` as routing information, not authenticated identity. Do not send an automatic reply. Use the same envelope for all transports. Do not change watcher or timer event formats.

## R3 - tmux

Discover pane ID from TMUX_PANE and socket from the actual tmux server. Verify live session association using more than pane existence (process identity and trusted registration evidence). Verify again before delivery. Use literal text and safe submission; never send Enter to an approval prompt or arbitrary shell. Do not claim busy or idle from pane existence. No tmux dependency if native delivery works. No implicit fallback to another harness. Test custom sockets, pane reuse, stale descriptors, multiline payloads and approval state.

## R4 - Output

Human output states target, selected transport and delivery result without logging full message content by default. A native queue acceptance is not evidence that the agent woke or processed it. Document version-specific wake/queue behavior. Report unsupported or uncertain paths explicitly.
