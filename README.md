# Claude Code Config

My global [Claude Code](https://docs.anthropic.com/en/docs/claude-code) configuration — instructions, custom skills, and cross-project memory that persist across all conversations.

## What's Here

```
~/.claude/
├── Claude.MD              # Global instructions (loaded in every conversation)
├── settings.json          # Runtime settings (plugins, env vars)
├── skills/                # Custom slash-command skills
│   ├── creating-linear-tickets/
│   ├── linear-todo-runner/
│   ├── plan-review-ceo/
│   ├── plan-review-eng/
│   ├── starting-linear-ticket/
│   └── verify-library-api/
└── projects/              # Per-project memory (feedback, workflow learnings)
    └── -Users-.../memory/
```

## Global Instructions (`Claude.MD`)

The main config file. Sets behavioral rules that apply to every project:

- **Skills-first** — always check for an applicable skill before acting
- **Clarify before acting** — ask questions and state a plan before writing code
- **TDD** — write tests before implementation, no exceptions
- **Systematic debugging** — investigate root causes before proposing fixes
- **API verification** — check installed library versions before assuming API patterns
- **Linear integration** — track work with Linear tickets, vertical slice scoping
- **Git workflow** — never commit to main; always use worktrees, branches, and PRs
- **Subagent delegation** — dispatch independent implementation tasks to parallel agents

## Skills

Custom skills extend Claude Code with structured workflows. Invoked with the `Skill` tool or as slash commands.

### `verify-library-api`

Prevents assuming outdated API patterns. Checks installed version, verifies API against that version (reading `node_modules`/`site-packages` or searching docs), and includes version-check instructions when spawning sub-agents.

### `plan-review-ceo`

Three-phase scope review: **EXPAND** (dream big, explore adjacent opportunities) → **HOLD** (lock scope, draw the line) → **REDUCE** (cut to essentials). Produces "building now / building later / not building" lists. One question at a time, opinionated recommendations.

### `plan-review-eng`

Technical review with two modes:

- **Planning mode** — architecture review: component boundaries, data flow, failure modes, dependency graph
- **Execution mode** — code quality, test strategy, performance review against actual code

### `creating-linear-tickets`

End-to-end workflow for turning ideas into well-scoped Linear tickets: brainstorm → CEO review → eng review → scope assessment → ticket creation. Includes a fast path for obvious, small-scope changes.

### `starting-linear-ticket`

Complete ticket workflow: fetch from Linear → mark in progress → create worktree → brainstorm design → create task list → TDD implementation with subagents → verify → PR → code review → CI → update Linear. Supports team-based parallel execution for multiple independent tickets.

### `linear-todo-runner`

Batch ticket processor. Fetches all Todo issues, maps dependencies, then runs a rolling queue of up to 4 parallel agents — each working through the full ticket workflow independently. Agents propose acceptance criteria and wait for approval before implementing.

## Memory System

Claude Code's auto-memory stores learnings from past conversations. Organized by type:

- **Feedback** — corrections and confirmed approaches (e.g., "background subagents need `mode: acceptEdits`")
- **User** — role, preferences, expertise level
- **Project** — ongoing initiatives, deadlines, decisions
- **Reference** — pointers to external resources (Linear projects, Notion docs, dashboards)

Memory lives in `projects/<encoded-path>/memory/`. Each project gets its own memory directory. Project-specific references (API keys, deployment IDs, infrastructure details) belong in each project's own `.claude/CLAUDE.md`, not here.

## Settings

`settings.json` configures runtime behavior:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "enabledPlugins": {
    "superpowers@superpowers-marketplace": true
  },
  "effortLevel": "high"
}
```

- **Agent teams** — enables multi-agent coordination for parallel ticket work
- **Superpowers plugin** — adds structured workflow skills (TDD, debugging, brainstorming, code review, git worktrees, etc.)
- **Effort level** — sets reasoning depth to high

## Superpowers Plugin

The [superpowers](https://github.com/anthropics/claude-code-superpowers) plugin adds foundational workflow skills that the custom skills build on:

- `brainstorming` — structured exploration before implementation
- `test-driven-development` — RED → GREEN → REFACTOR cycle
- `systematic-debugging` — multi-phase investigation before fixing
- `writing-plans` — implementation plans with review checkpoints
- `verification-before-completion` — evidence before assertions
- `using-git-worktrees` — isolated feature workspaces
- `finishing-a-development-branch` — merge/PR/cleanup guidance
- `requesting-code-review` / `receiving-code-review` — structured review workflows
- `dispatching-parallel-agents` / `subagent-driven-development` — parallel execution

## Per-Project Setup

Each project repo has its own `.claude/CLAUDE.md` with project-specific instructions (tech stack, verification commands, deployment details, infrastructure references). The global config here provides the workflow framework; project configs provide the domain context.

Projects can also define their own skills in `.claude/skills/` that override or extend the global ones.

## Design Philosophy

**Workflows over prompts.** Instead of hoping Claude remembers the right approach, skills encode proven workflows as structured sequences with explicit checkpoints. The global instructions enforce skill usage — Claude must check for applicable skills before any action.

**Vertical slices.** Tickets, skills, and agent work all follow the same principle: deliver complete, usable increments rather than horizontal layers.

**Trust but verify.** Subagents handle implementation autonomously, but must run verification gates (tests, type checks, linting) and report evidence before claiming success. The lead agent never writes code directly.

**Memory as feedback loop.** Corrections and confirmed approaches are saved as memories so the same guidance doesn't need to be repeated across conversations. General workflow learnings stay global; project-specific details stay in project repos.
