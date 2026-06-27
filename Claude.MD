# Global Claude Code Instructions

## Superpowers (Skills)

**🚨 ALWAYS USE SUPERPOWERS - Check for applicable skills BEFORE any action 🚨**

If there's even a 1% chance a skill applies, invoke it with the `Skill` tool. Don't rationalize or skip.

**Common skills**: `brainstorming`, `systematic-debugging`, `test-driven-development`, `writing-plans`, `verification-before-completion`, `requesting-code-review`, `using-git-worktrees`, `finishing-a-development-branch`, `verify-library-api`, `starting-linear-ticket`, `fixtest`

### Subagents for Implementation

When implementing tasks from a task list, **use subagents** (`Task` tool, `subagent_type: "general-purpose"`) instead of doing each task sequentially yourself. Dispatch independent tasks in parallel. Include full context in each subagent prompt: worktree path, files to modify, acceptance criteria, and TDD instructions. See the `starting-linear-ticket` skill Step 6 for the prompt template.

### Agent Instructions for Framework-Specific Tasks

When spawning explore or implementation agents that analyze framework-specific code (middleware, config, routing, etc.), always include:

> Check the installed version of the framework in package.json or node_modules before making claims about conventions. If anything doesn't match expected patterns, use WebSearch to look up docs for that specific version. Do NOT rely on training knowledge for framework conventions — flag uncertainty rather than asserting code is broken.

This prevents agents from confidently misidentifying newer patterns (e.g., Next.js 16's `proxy.ts`) as broken code.

---

## Clarify Before Acting

**Default to asking questions, not making assumptions.**

Before starting any non-trivial task:
1. **State your understanding** of the goal — what should change and what should NOT change
2. **Define acceptance criteria** — if the user hasn't provided clear acceptance criteria, ask for them. Do not invent your own or start coding without knowing what "done" looks like.
3. **Ask clarifying questions** when any of these are true:
   - The requirement has multiple valid interpretations
   - You're unsure about edge cases or expected behavior
   - The task involves domain-specific logic (tiers, counts, implicit behavior)
   - There are no clear acceptance criteria
4. **Wait for confirmation** before writing code

Do NOT rationalize skipping this ("it's probably X", "I'll just try this approach"). The cost of one question is far less than the cost of implementing the wrong thing.

### Pre-Implementation Plan (mandatory)

**Before writing ANY implementation code**, state your plan in 3-5 bullet points and **wait for user approval**:

- **What you'll change** — files, components, endpoints, DB tables
- **What you WON'T touch** — explicitly call out boundaries
- **What tools/services you'll use** — Supabase, Railway, specific APIs, etc.
- **Key design decisions** — approach trade-offs, if any

This applies even when the path seems obvious. Do NOT skip this for "simple" tasks — wrong-approach corrections are the #1 source of wasted time. One checkpoint costs seconds; a wrong approach costs the whole session.

---

## Investigate Before Proposing Fixes

**REQUIRED:** Use the `superpowers:systematic-debugging` skill when encountering any bug, test failure, or unexpected behavior. Do not propose fixes without completing its investigation phases first.

---

## Verify APIs and Library Versions

**REQUIRED:** Use the `verify-library-api` skill before using any framework/library API. Do not assume API patterns are current — libraries change between versions.

---

## Testing (TDD)

**REQUIRED:** Always use Test-Driven Development. Use the `superpowers:test-driven-development` skill.

- Write tests **before** implementation code — no exceptions
- Every feature, bug fix, and refactor must include unit tests
- No PR should be created without passing tests
- Run `npm test` (or project-equivalent) before committing

---

## Task Tracking with Linear

The Linear team name is configured per-project in the project's `.claude/CLAUDE.md`.

### When to Create Tasks

Create a Linear task for non-trivial work: features, bugs, refactors, multi-file changes, or anything taking >5 minutes.

### Ticket Scoping — Vertical, Complete Features

**Tickets should be vertical slices of user-facing functionality, not horizontal layers.**

- **Good:** "Linear Integration — OAuth, sync tasks as backlog, settings UI" (one ticket delivers a complete feature)
- **Bad:** "Linear OAuth flow", "Linear sync API route", "Linear settings UI" (three tickets that each deliver nothing usable alone)

**Guidelines:**
- Each ticket should deliver a complete, usable feature when done
- Include backend + frontend + tests in a single ticket
- **Include analytics instrumentation in the slice design.** If a ticket changes user-facing behavior, its design must name the metric it intends to move and include the analytics/PostHog events needed to measure it — added in the same slice, not deferred. A behavior change you can't measure isn't a complete slice. "Measure later" reliably becomes "never measured."
- A user should be able to see/use the result of a completed ticket
- Don't split by technical layer (API route, component, hook, store) — split by user value
- It's OK for feature tickets to be larger; use subtasks or task lists within the ticket for tracking

**Exceptions:** Infrastructure/setup tickets (DB migrations, auth setup, CI config) can be horizontal since they're prerequisites.

### Creating Tasks

```
mcp__linear-server__create_issue with:
- title: "Task title"
- description: "Task description with context"
- team: "<team-name>"  # See project CLAUDE.md
- state: "Backlog"
- priority: 1-4 (1=Urgent, 2=High, 3=Medium, 4=Low, 0=No priority)
- labels: ["Bug" | "Feature" | "Improvement"]
```

**Label Guidelines:**
- **Bug**: Fixes for incorrect behavior, errors, or issues
- **Feature**: New functionality or capabilities
- **Improvement**: Enhancements to existing functionality (performance, UX, code quality)

### Updating Tasks

**CRITICAL**: Update Linear as you work:
- Starting work → `state: "In Progress"`
- PR created → `state: "In Review"`, add PR URL to description
- PR merged → `state: "Done"`
- Blocked → Add "blocked" label, move to "Backlog" state
- Unblocked → Remove "blocked" label

Search → Get issue → Update with `mcp__linear-server__update_issue`.

**Note**: Always preserve the Bug/Feature/Improvement label when updating tasks.

### Linear vs TodoWrite

- **Linear**: Track overall features/bugs across sessions
- **TodoWrite**: Track in-session progress

Use both together.

### Timeouts

If Linear MCP times out, ask user to run `/mcp` to re-authenticate.

---

## Git Workflow

**🚨 CRITICAL: NEVER commit directly to `main`. ALWAYS use a worktree and create a PR. 🚨**

Even for "quick fixes" or single-file changes - ALWAYS:
1. Use `using-git-worktrees` skill to create isolated worktree
2. Do ALL work in the worktree (not the main directory)
3. Make commits on the branch
4. Push the branch
5. Create a PR with `gh pr create`
6. Wait for user approval before merging

**NO EXCEPTIONS.** Do not commit to main, even if the user says "commit" or "push". Create a worktree and PR instead.

### Branch Names
- `feature/<description>` - New features
- `fix/<description>` - Bug fixes
- `refactor/<description>` - Refactoring
- `docs/<description>` - Documentation
- `chore/<description>` - Maintenance

### Workflow
1. Create/find Linear task, **update to "In Progress"** before starting any design or implementation work
2. **Update main branch** to latest:
   ```bash
   git fetch origin
   git checkout main
   git pull origin main
   ```
3. **Create isolated worktree** (use `using-git-worktrees` skill)
   - Creates clean workspace without affecting main directory
   - Creates branch from updated main
   - Runs setup (npm install, etc.) and verifies tests pass
   - Worktree created at `.worktrees/<branch-name>` or configured location
4. Make commits (reference task: "PROJ-5: Add feature")
5. Push: `git push -u origin feature/descriptive-name`
6. Create PR with `gh pr create`
7. Update Linear task with PR link and "In Review" status
8. Verify CI passes: `gh pr checks <pr-number>`

### Git Worktrees

**When to use:** All feature work that requires isolated workspace.

**Always use the `using-git-worktrees` skill** - it handles:
- Directory selection (`.worktrees/` vs global location)
- .gitignore verification for project-local directories
- Branch creation
- Project setup (npm install, pip install, etc.)
- Baseline test verification

**After work complete:** Use `finishing-a-development-branch` skill for cleanup.

### Using Teams for Parallel Work

Use `TeamCreate` to spawn parallel agents when:
- **Multiple independent tickets** — 2+ tickets with no shared dependencies (each agent gets its own worktree and runs the full workflow)
- **Cross-repo changes** — A single ticket touching multiple repos. Each agent works in its own repo/worktree.
- **Large ticket with separable subtasks** — Independent pieces that don't block each other

**Don't use teams when:**
- Single ticket in a single repo
- Tightly coupled sequential changes (schema → backend → frontend in order)
- Small/quick tickets where coordination overhead exceeds the benefit

The `starting-linear-ticket` skill has full team setup details.

### PR Requirements
- Link to Linear task
- Test plan
- Run tests locally before pushing
- Verify CI passes

### Merging

**🚨 NEVER MERGE WITHOUT EXPLICIT USER APPROVAL 🚨**

Wait for user to say "merge" or "merge the PR", then:
```bash
gh pr merge <pr-number> --squash --delete-branch
```

---

## Supabase MCP

If Supabase MCP tools consistently timeout:
1. Stop retrying
2. Ask user to run `/mcp` to re-authenticate
3. Provide SQL for manual execution

---

## Task Completion

When completing tasks, update:
1. **Linear** - Status to "Done", add PR link to description
2. **Docs** - Update CLAUDE.md if behavior changed

---

## Pushing Configuration Changes

**After modifying files in `~/.claude/`** (CLAUDE.md, skills, project settings):

The `~/.claude/` directory is a separate git repo (`kmigdol/claude-config`). Changes must be pushed there (not to project repos):

```bash
cd ~/.claude && git add -A && git commit -m "<description>" && git push
```

**Note:** Git tracks the file as `Claude.MD` (not `CLAUDE.md`).
