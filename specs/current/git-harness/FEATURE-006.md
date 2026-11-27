# Configuration and lifecycle integration

## R1 - config

Write a short managed block to AGENTS.md in current directory. --config-dir selects directory for harness integrations (default current directory). --harness repeatable selects one or more, default all. --dry-run shows files and changes without writes. Merge valid existing settings and preserve unrelated hooks/plugins. Refuse invalid files; do not overwrite user-owned content. Repeated config is idempotent. Use a pinned executable/version and cached or installed invocation for time-limited hooks; report missing executable or trust. Do not auto-trust hooks, install global config, or change permissions. Add Git ignore rules for temporary session artifacts without ignoring persistent history; honor configured directory names. Preserve symlinks. Document how to install links or explicit config at nested launch directories where harness does not inherit ancestor config.

Managed block (keep under 100 words):

```markdown
<!-- git-harness:begin -->
## Agent communication
Use `uvx git-harness message --target PATH "TEXT"` to contact a running agent. Use `uvx git-harness check --target PATH` to check availability. Run `uvx git-harness prime` for usage. Lifecycle integrations register sessions. If registration is missing, run `uvx git-harness init` inside the session.
<!-- git-harness:end -->
```

## R2 - prime

Print concise Markdown (target <=200 words) with init, check, run, stop, message, watcher, timer, sync, config and help examples; explain default target and foreground/background. Use `--from .` when a reply is necessary. To reply, use the received `from` value as `--target`. No model calls or filesystem mutation.

## R3 - Lifecycle

Integrations use deterministic commands only. Startup/resume calls init with verified native ID, fixed launch target and owner evidence; shutdown calls sync if enabled, then stop even if sync fails. Respect native timeout; do not depend on shutdown sync for data durability. Use a guard that identifies the specific runtime, including same-ID resume. Repeated hooks must not replace a live registration or stop a newer owner. Distinguish compaction, reload, fork, session switch and actual exit; document verified behavior per harness. Do not register subagents or other conversations accidentally. On crash, run and init reconcile. Hook stdout must conform to native protocol; diagnostics go to stderr.

## R4 - Nested and regular projects

No role names or directory conventions beyond target resolution in core. Test standard repo and repo/agents/role/1 and /2 with common config. Register each launch directory independently, never the config root. Where discovery is not inherited, config must report the required local link/config and provide exact tested instructions. Do not recursively modify arbitrary nested directories. Existing agent role skills remain optional consumers.
## R5 - Resource ownership

The config command calls the common Harness.configure interface. Each harness owns its integration resources in its Python package and knows the native installation paths. Use importlib.resources to read packaged files. Build Codex and Claude hook fragments as Python dictionaries in their adapters. Do not ship hooks.json or settings.json templates. Keep OpenCode TypeScript with OpenCode and Pi TypeScript with Pi. Keep additional helper assets with the harness that uses them. Do not put these resources in a shared templates directory. Keep managed AGENTS.md text and prime output in their command modules or shared harness-neutral functions. The config command MUST NOT contain harness-specific installation branches. Test resource access from an installed wheel.

## R6 - Selective configuration merge

Read the existing user configuration before a write. Create a file only if it does not exist. Update only entries owned by git-harness. Identify these entries by a stable, documented command signature. Preserve unrelated hook entries, matchers, order and other settings. Do not replace a complete lifecycle event array. Do not use a generic recursive merge for arrays. Reject invalid JSON or incompatible structures before a write. Do not change files that already have the required configuration. Use atomic writes. Do not change a user-owned TypeScript file that has a conflicting name. Test first install, repeated install, upgrade, unrelated hooks, invalid JSON and dry-run.
