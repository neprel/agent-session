# Implementation graph

Task dependency metadata is authoritative. This graph is a derived planning view. Use parallel work only in isolated checkouts.

```mermaid
graph TD
  A1["AS-001: Verify harness interfaces and upstream history code"]
  A2["AS-002: Create package and shared CLI contracts"]
  A3["AS-003: Implement target and registration lifecycle"]
  A4["AS-004: Implement shared delivery and tmux fallback"]
  A5["AS-005: Implement worker process records and stop"]
  A6["AS-006: Implement filesystem watcher"]
  A7["AS-007: Implement timer"]
  A8["AS-008: Implement canonical history storage"]
  A9["AS-009: Implement sync and run core"]
  A10["AS-010: Implement config and prime"]
  A11["AS-011: Implement Codex adapter"]
  A12["AS-012: Implement Claude adapter"]
  A13["AS-013: Implement OpenCode adapter"]
  A14["AS-014: Implement Pi adapter"]
  A15["AS-015: Integrate lifecycle and cross-harness history"]
  A16["AS-016: Prepare release candidate"]
  A17["AS-017: Implement isolated test foundation"]
  A18["AS-018: Implement GitHub CI and release workflows"]
  A19["AS-019: Complete Git Harness rename"]
  A2 --> A19
  A17 --> A19
  A2 --> A17
  A17 --> A3
  A17 --> A18
  A18 --> A16
  A1 --> A2
  A2 --> A3
  A3 --> A4
  A3 --> A5
  A4 --> A6
  A5 --> A6
  A4 --> A7
  A5 --> A7
  A2 --> A8
  A3 --> A8
  A4 --> A9
  A8 --> A9
  A3 --> A10
  A5 --> A10
  A1 --> A11
  A4 --> A11
  A9 --> A11
  A10 --> A11
  A1 --> A12
  A4 --> A12
  A9 --> A12
  A10 --> A12
  A1 --> A13
  A4 --> A13
  A9 --> A13
  A10 --> A13
  A1 --> A14
  A4 --> A14
  A9 --> A14
  A10 --> A14
  A6 --> A15
  A7 --> A15
  A11 --> A15
  A12 --> A15
  A13 --> A15
  A14 --> A15
  A15 --> A16
```

## Strategy

Verify native contracts first. Define both common interfaces and all ten command modules before parallel implementation. Keep each harness implementation and its resources in one package. Implement registration and worker ownership before triggers. Implement history storage and run core before native adapters. Integrate and verify all routes before release. The manager may split tasks further without changing requirements.

Implement AS-017 immediately after AS-002. Run AS-018 as soon as the test foundation is available; complete its native matrix as adapters become available. AS-016 requires AS-015 and AS-018. Do not publish during implementation.

Owner ordered AS-019 before resuming AS-003. Existing task IDs and dependency metadata are unchanged. AS-018 remains open for its full native gates.
