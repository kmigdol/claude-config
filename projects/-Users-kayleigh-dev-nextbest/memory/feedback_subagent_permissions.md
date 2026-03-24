---
name: Subagent permission mode
description: Background subagents need mode acceptEdits to avoid permission denial on Edit/Write/Bash tools
type: feedback
---

Background subagents must be launched with `mode: "acceptEdits"` (or `"bypassPermissions"`), not `"auto"`.

**Why:** Background agents can't prompt the user for interactive tool approval. With `mode: "auto"`, Edit/Write/Bash tools get auto-denied, causing the agent to fail silently.

**How to apply:** When dispatching implementation agents (subagents that need to write code/run tests), always use `mode: "acceptEdits"`. This applies to any agent launched with `run_in_background: true`.
