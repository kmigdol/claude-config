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

**Every ticket passes three gates before creation** (full detail in the `creating-linear-tickets` skill — they apply to ad-hoc ticket creation too):
1. **Outcome first** — the ticket opens with an `## Outcome` section: what changes for a user/the business and the observable that proves it. Can't write one → it's a task inside an existing ticket, not a ticket. **The title carries the same burden** — see Ticket Titles below.
2. **Reopen, don't refile** — if the justification is "still broken after NEX-YYY", reopen NEX-YYY; don't file a new ticket that lets it stand as Done.
3. **No AC discharge** — a split-off ticket may not carry the parent's goal-completing work (remediation, measurement, e2e coverage never split off). An AC is never satisfied by filing a ticket for it.

### Ticket Titles — One Imperative Statement of the Change

**A title says what the ticket does, not what is broken today.** A symptom-framed title ("X silently breaks Y", "Z crashes under load", "W is all-or-nothing") describes the world we're leaving, so it reads as accurate forever — including after the fix ships — and a backlog of them is a list of complaints rather than intended changes.

**Format:** one imperative sentence naming the change, in concrete nouns. Optional `Area:` prefix. **No trailing em-dash clause explaining or justifying it.**

These are the calibration — copy their shape:

- "Cut daily pipeline cron over from Railway to Prefect schedule" (NEX-390)
- "Product variants: link distinct sibling SKUs into a family + \"Other variants\" on product pages" (NEX-487)
- "Fold refresh-retailers into the daily Prefect pipeline as a (non-fatal) stage" (NEX-392)

Each is a single statement of what gets built. Note what's absent: no symptom, no rationale, no metric, no file path, no "— because Y". NEX-487 runs long because it's naming two deliverables, which is fine; length is only a problem when it comes from *explaining*.

| Instead of (symptom-framed) | Write (one imperative statement) |
|---|---|
| "A killed pipeline run silently suppresses the next 20 hours of runs — the debounce marker records started, never finished" | "Stop a killed run from skipping the next day's pipeline" |
| "Catalog cache invalidation is all-or-nothing — every publish regenerates all 1,811 pages regardless of what changed" | "Rebuild only the pages a publish changed" |
| "/admin/taxonomy crashes during rapid approval bursts" | "Keep /admin/taxonomy up during approval bursts" |
| "Renaming a product in the catalog leaves its old name live" | "Stop serving a product's old name after a rename" |

**The em-dash clause is the wordiness generator.** `<change> — <the symptom it fixes>` is the shape to avoid; it doubles the length to restate what `## Problem` already says. If the verb feels too thin to stand alone, fix the verb — don't prop it up with a second clause.

**The verb names the change a user or the business would notice, not an implementation step.** "Emit a completion marker", "Add an `updated_at` column", "Coalesce the refresh calls" all fail that test — they're steps inside the work, not its point. When the honest verb is a pure-mechanism one, the title is telling you this is a task inside another ticket, not a ticket (Gate 1).

**The problem still gets written down** — in `## Problem`, at full detail, with the production evidence. Not in the title, and neither are file paths, line numbers, or metrics. Symptom-first phrasing belongs to the *incident*; the ticket is for the *fix*.

Ticket titles are the one place all three gates are visible at a glance, so read a new title against them: a title naming only a symptom or a mechanism is a Gate 1 miss; a title that reads "…still broken after NEX-YYY" is a Gate 2 miss (reopen it); a title naming only remediation/measurement/e2e split off a parent is a Gate 3 miss.

**This is enforced by a hook, not by memory.** `~/.claude/hooks/linear-title-check.py` runs `PreToolUse` on `mcp__.*__save_issue` (both Linear MCP servers) and **blocks the call** on the mechanically-decidable failures: an explanatory ` — ` clause, over 100 characters, or a leading article/gerund. The block message is fed back so the title gets rewritten and retried; a `save_issue` that doesn't set a title passes straight through. It catches the shape, not the judgment — deciding whether the verb names something a user or the business would notice is still yours. To inspect or disable it, see `/hooks`.

**Do NOT create a new ticket for work that's needed to accomplish an existing ticket's goal.** If a piece of work helps accomplish the original goal of a ticket — and you can't accomplish that goal without it — it belongs IN that ticket, even when you discover the need mid-work or after the ticket was (prematurely) closed. Reopen the ticket rather than filing a follow-up. New tickets are only for **genuinely separate/additional outcomes**, not for finishing the one you're on. (Fragmenting goal-completing work across tickets lets the original read "Done" when its goal isn't met and buries the remaining work.)

### Marking a Ticket Done — Verify Every Acceptance Criterion First

**Merging a PR, or the user saying "good to merge," is NOT the same as the ticket being Done.** Before flipping any ticket to Done, re-read its acceptance criteria and confirm **each one is actually met, with evidence** — not vibes. Post the audit as a Linear comment (`AC audit: 1 ✅ …, 2 ❌ dropped per user <date>`). **An AC "handled" by filing a follow-up ticket is NOT met** — either the work happens in this ticket, or the AC is deliberately dropped with user sign-off, on the record. If any AC is unmet (e.g. a coverage/quality metric is only partially there and you're still working it), the ticket stays **In Progress**. "PR merged" ≠ "ACs verified" ≠ "Done". If you catch yourself still working toward the goal after marking Done, you closed too early — reopen it.

**A shipped ticket that named a metric goes to `Monitoring`, not `Done`.** Shipping is not the outcome — the metric moving is. On merge, land it in `Monitoring` and leave it there until a human reads the number. `Done` requires shipped AND measured. Only work with nothing to measure (refactors, types, tooling, docs, CI) goes straight to `Done`.

The `metrics-review` scheduled task posts a daily reading on every `Monitoring` ticket. It is **report-only** and never moves tickets. Leaving `Monitoring` is a judgement call: metric improved + all ACs re-verified → `Done`; regressed → `In Progress` or revert. **Elapsed time is never a reason to close** — "it's been a week" is not a result. And at this traffic level there is no significance to find, so read slope and funnel health directionally, and name any confounder that shipped into the same surface in the same window rather than claiming an attributable result.

**Linear's GitHub integration will fight you here.** It moves a ticket when its PR merges — if that's pointed at `Done`, tickets auto-close seconds after merge, before any metric exists. Point it at `Monitoring` (Settings → Integrations → GitHub). If you see a ticket close itself on merge, move it back; that flip is not a verification.

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

**🚨 EVERY ticket goes through the `creating-linear-tickets` skill — no exceptions. 🚨** Invoke it with the `Skill` tool before creating ANY Linear ticket: planned features, quick bugs, follow-ups discovered mid-work, tickets the user dictates verbatim. The skill enforces the three gates above and has a fast path for small, well-scoped tickets — so "it's just a quick ticket" is never a reason to bypass it. Do NOT call `create_issue`/`save_issue` directly to create a ticket; the template below is what the skill produces, kept here as a field reference only.

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
- PR merged → `state: "Monitoring"` (named a metric) or `state: "Done"` (nothing to measure)
- Metric read and all ACs re-verified → `state: "Done"`
- Blocked / deliberately deferred → Add the **`parked`** label, move to `"Backlog"` state, and **write the unpark trigger in a comment**
- Unparked → Remove the `parked` label, restore the prior state

**There is no `blocked` label.** This file said there was until 2026-08-17, and `save_issue` hard-rejects an unresolvable label name (it replaces the whole set, so it refuses rather than silently dropping) — so following the old instruction failed the call outright. The Nextbest workspace has exactly five issue labels: `parked`, `SEO`, `Bug`, `Feature`, `Improvement`. **Confirm with `list_issue_labels` before using any label not in that list** — labels are per-workspace and this list will drift.

`parked` is also the better concept. Its definition: *"Deliberately deferred with a written unpark trigger — not backlog, not cancelled. The idea is sound; the timing isn't."* **The written trigger is the point** — a parked ticket without a stated condition that brings it back is just a backlog item with extra styling. Write the condition as an *observable*, never a date: "the 08-19 read shows a non-zero link CTR", not "after the 19th". A date alone unparks the ticket whether or not the thing it was waiting on ever happened. (2026-08-17: NEX-651 and NEX-652 were parked behind NEX-650's kill-signal read on exactly these terms.)

Search → Get issue → Update with `mcp__linear-server__update_issue`.

**Note**: Always preserve the Bug/Feature/Improvement label when updating tasks — `labels` replaces the full set, so pass the existing ones back explicitly alongside any you add.

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
