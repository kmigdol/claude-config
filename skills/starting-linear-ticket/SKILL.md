---
name: starting-linear-ticket
description: Use when starting work on a Linear ticket - full workflow from fetch to PR creation including worktree setup, brainstorming, TDD implementation, and Linear status updates
---

# Starting Work on a Linear Ticket

## Overview

Complete end-to-end workflow for Linear tickets: fetch → in progress → worktree → brainstorm → (UI prototype) → task list → TDD → verify → PR → code review → CI → in review.

**Announce at start:** "I'm using the starting-linear-ticket skill to set up for this ticket."

## Required Input

User provides ticket identifier (e.g., "PROJ-63", "start PROJ-63", or just the number if context is clear).

## When to Use a Team

Before starting the workflow, evaluate whether this work should use a **team of parallel agents**. Use a team when:

### Use a Team When

- **Multiple independent tickets** — User asks to work on 2+ tickets at once. Each agent gets its own worktree and runs the full workflow independently.
- **Cross-repo changes** — A single ticket requires changes across multiple repos. Each agent works in a different repo/worktree.
- **Large ticket with independent subtasks** — A ticket has clearly separable pieces (e.g., "add 3 new API endpoints" where each endpoint is independent).

### Don't Use a Team When

- **Single ticket, single repo** — Standard workflow is sufficient.
- **Tightly coupled changes** — Work where each step depends on the previous step's output (e.g., schema change → backend update → frontend update in sequence).
- **Small or quick tickets** — The overhead of team coordination exceeds the benefit.

### Team Setup

When using a team, the lead agent should:

1. **Fetch all tickets** from Linear first to understand scope and dependencies
2. **Create a team** with `TeamCreate`
3. **Create tasks** from ticket requirements with `TaskCreate`
4. **Spawn teammate agents** with `Task` tool (`subagent_type: "general-purpose"`, include `team_name`)
   - Each teammate gets: ticket ID, requirements, acceptance criteria, target repo, branch name
   - Each teammate runs the full workflow (worktree → brainstorm → TDD → verify → PR → code review)
5. **Coordinate** — monitor progress, resolve blockers, handle cross-repo dependencies
6. **Report back** — collect PR URLs and update all Linear tickets

### Team Agent Naming

Name agents by their responsibility:
- `proj-140-agent` — for ticket-based agents
- `frontend-agent` / `backend-agent` / `pipeline-agent` — for repo-based agents

### Example: Multiple Tickets

```
User: "Start PROJ-140, PROJ-141, and PROJ-142"

Lead:
  1. Fetch all 3 tickets from Linear
  2. Verify they're independent (no blocking dependencies)
  3. Mark all 3 as "In Progress"
  4. TeamCreate → "proj-batch"
  5. Spawn 3 agents, each with full ticket context
  6. Each agent: worktree → brainstorm → TDD → verify → PR → code review
  7. Lead collects PRs, updates Linear to "In Review"
```

### Example: Cross-Repo Ticket

```
User: "Start PROJ-150" (requires changes across multiple repos)

Lead:
  1. Fetch ticket, brainstorm overall design
  2. Identify which changes go to which repo
  3. TeamCreate → "proj-150"
  4. Spawn agents per repo with their slice of the design
  5. Define task dependencies (e.g., backend blocked by schema changes)
  6. Each agent creates a PR in their respective repo
  7. Lead links all PRs in Linear ticket
```

## Workflow

```dot
digraph workflow {
    rankdir=TB;

    fetch [label="1. Fetch ticket", shape=box];
    progress [label="2. Mark In Progress", shape=box];
    worktree [label="3. Create worktree", shape=box];
    rich [label="Ticket has Verification\n+ Snapshot sections?", shape=diamond];
    brainstorm [label="4. Brainstorm design\n(legacy ticket)", shape=box];
    eng [label="4. Eng Review (execution)\nrich ticket: skip brainstorm", shape=box];
    fresh [label="4.5. Snapshot Freshness Check\n(rich ticket only)", shape=box];
    proto [label="4.7. UI Prototype Check\n(if substantial UI)", shape=box, style=dashed];
    todos [label="5. Create task list", shape=box];
    tdd [label="6. Implement with TDD", shape=box];
    verify [label="7. Verify (tests + manual)", shape=box];
    pr [label="8. Create PR", shape=box];
    codereview [label="9. Code review", shape=box];
    ci [label="10. Check CI", shape=box];
    localtest [label="11. Local deploy\n(if UI feature)", shape=box, style=dashed];
    review [label="12. Update Linear\nto In Review", shape=box];

    merge [label="13. Merge & Cleanup\n(/merge)", shape=box, style=dashed];

    fetch -> progress -> worktree -> rich;
    rich -> eng [label="yes"];
    rich -> brainstorm [label="no"];
    brainstorm -> eng;
    eng -> fresh -> proto -> todos;
    todos -> tdd -> verify -> pr -> codereview -> ci -> localtest -> review -> merge;
}
```

### Step 1: Fetch Ticket from Linear

```
mcp__linear-server__get_issue with id: "<ticket-id>"
```

Extract and summarize:
- **Title**
- **Description** (requirements, acceptance criteria)
- **Labels** (Bug, Feature, Improvement)
- **Priority**
- **Any linked issues or dependencies**

If ticket not found or MCP timeout: ask user to verify ticket ID or run `/mcp`.

**Check for acceptance criteria.** If the ticket does NOT have clear acceptance criteria (specific, testable conditions that define "done"), STOP and ask the user to provide them before proceeding. Do not invent acceptance criteria or proceed without them — they drive the design, tests, and verification steps downstream.

### Step 2: Mark as In Progress

```
mcp__linear-server__update_issue with:
- id: "<ticket-id>"
- state: "In Progress"
```

Preserve existing labels (Bug/Feature/Improvement).

### Step 3: Create Git Worktree

**REQUIRED:** Invoke `superpowers:using-git-worktrees` skill.

Use branch name from Linear if available (`branchName` field), otherwise generate:
- Feature: `feature/<prefix>-<number>-<slug>`
- Bug: `fix/<prefix>-<number>-<slug>`
- Improvement: `improve/<prefix>-<number>-<slug>`

Where `<slug>` is kebab-case from ticket title.

### Step 4: Design Pass (Conditional Brainstorm + Eng Review)

**Inspect the ticket for new-template sections:**

- `## Verification` (with Observable Signals + Test Scenarios + Post-Merge Verification)
- `## Implementation Snapshot` (with `As of <SHA>` marker)

**Path A — Ticket has both sections (rich ticket from `creating-linear-tickets`):**
- **Skip `superpowers:brainstorming`.** The ticket already encodes intent, observable signals, and codebase anchors. Asking clarifying questions defeats the autonomy goal.
- Go directly to `plan-review-eng` in **execution mode** for a sanity pass on the snapshot-anchored approach. The reviewer reads the ticket's Snapshot + Verification, looks at the actual files, and surfaces edge cases / perf concerns / test gaps the ticket creator couldn't see.
- If the eng review surfaces a real ambiguity (not just suggestions), STOP and escalate to the user. Otherwise proceed to Step 4.5.

**Path B — Ticket is missing Verification or Implementation Snapshot (legacy / hand-written):**
- **REQUIRED:** Invoke `superpowers:brainstorming` skill (current behavior).
  - Ask clarifying questions one at a time
  - Propose 2-3 approaches with trade-offs
  - Present design incrementally for validation
  - Write design doc to `docs/plans/YYYY-MM-DD-<topic>-design.md`
- Then invoke `plan-review-eng` in **execution mode**.

**Both paths produce:** edge cases to handle, codepath diagram with test coverage mapping, perf concerns, and an updated test plan matching the acceptance criteria. The test plan feeds Step 6 (TDD implementation).

### Step 4.5: Snapshot Freshness Check (Path A only)

The Implementation Snapshot in the ticket was captured at ticket-creation time. Before trusting it, run the lightweight probes in `freshness-check.md`:

- Each path under "Files to modify" / "Files to create" exists (or is correctly marked as new).
- Each "see `<symbol>` in `<path>`" reference still resolves (grep for the symbol at that path).
- Each "Schema touched" column still exists (one Supabase MCP query against `information_schema.columns`).

**If all probes pass:** trust the snapshot. Proceed.

**If any probe fails:** spawn a Rescue Scout subagent (Agent tool, `subagent_type: "general-purpose"`, brief from `~/.claude/skills/creating-linear-tickets/scout-prompt.md` "Rescue Scout" mode). It refreshes only the broken anchors and writes the refreshed snapshot to `<worktree>/SNAPSHOT.md`. The Linear ticket is NOT updated — the durable spec hasn't changed.

After rescue, the implementing agent uses the refreshed snapshot for the rest of the workflow.

### Step 4.7: UI Prototype Check (conditional — visually substantial UI only)

**When:** The ticket introduces or significantly reworks user-facing UI — a new page, a redesigned surface, new card/list layouts, a non-trivial component. **Skip when:** backend/pipeline-only work, type-only changes, copy tweaks, or small CSS adjustments — the cost isn't worth it there.

**Why:** A 5-minute throwaway prototype catches "this isn't the layout I pictured" *before* you've written components, tests, and an approval flow against the wrong design. Wrong-look corrections after the build are the expensive ones.

**How:**
1. Build a single self-contained throwaway artifact (one HTML file with inline CSS/JS is usually enough; or a quick Storybook/page stub) that renders the proposed layout. **Use real data where you can** — query the actual DB / API so the look is faithful to production content, not lorem-ipsum. Keep it disposable; this is not production code and gets no tests.
2. Render it and capture screenshots at **both** the project's desktop and mobile breakpoints (e.g. 1280×800 + 375×812). Drive a real browser (claude-in-chrome MCP or a local static server) — don't reason about the look from the source.
3. Present the screenshots to the user and **get explicit sign-off on the look** (layout, hierarchy, lanes, wording) before proceeding. Fold any requested changes into the prototype and re-confirm.
4. Only then continue to the task list. The signed-off prototype becomes the visual reference for implementation — but the production build still follows TDD and the project's UI e2e rules (e.g. `boundingBox()` checks); the prototype does not replace those.

Delegate the prototype build to a subagent when the data is large or the artifact is involved (keeps the dataset out of the lead's context). The lead drives the browser screenshots and the user sign-off.

### Step 5: Create Task List

**REQUIRED:** Before writing any code, create a `TaskCreate` todo list that breaks the design into implementation tasks.

Based on the design from brainstorming, create tasks for:
- Each piece of functionality to implement (API endpoints, components, pages, etc.)
- A verification task (run full test suite + TypeScript + build)
- A PR creation task

Set up dependencies with `TaskUpdate` (e.g., verification blocked by implementation tasks, PR blocked by verification).

Update task status as you work: `in_progress` when starting, `completed` when done. This gives the user visibility into progress.

### Step 6: Implement with Subagents

**REQUIRED:** Use subagents (Task tool) to implement each task from the task list.

After creating the task list in Step 5, dispatch implementation tasks to subagents:

1. **Identify independent tasks** — tasks that don't depend on each other can run in parallel
2. **Dispatch each task** using `Task` tool with `subagent_type: "general-purpose"`
3. **Include full context** in each subagent prompt:
   - The worktree path (so they edit the right files)
   - Which files to modify and what changes to make
   - The acceptance criteria for that task
   - Instructions to follow TDD (RED → GREEN → REFACTOR)
4. **Run independent tasks in parallel** — launch multiple Task calls in a single message
5. **Run dependent tasks sequentially** — wait for blockers to complete first
6. **Update task status** — mark tasks `completed` as subagents finish

**Subagent prompt template:**
```
You are working in the worktree at: <worktree-path>

Task: <task description>

Files to modify:
- <file path> — <what to change>

Acceptance criteria:
- <criterion 1>
- <criterion 2>

## How to Work

1. Read the project's `.claude/CLAUDE.md` — it has a "Verification Commands"
   section with the exact commands you must run. These mirror CI.
2. Follow TDD:
   a. Write failing test first
   b. Implement minimal code to pass
   c. Refactor if needed

## Verification Gate (mandatory before reporting success)

Run ALL verification commands from the project's `.claude/CLAUDE.md`.
Every check must pass.

If any check fails:
1. Read the error output carefully
2. Diagnose the root cause (wrong approach vs. bug)
3. Fix the issue
4. Re-run ALL checks
5. Repeat up to 3 attempts

## Escalation

If after 3 fix attempts a check still fails, STOP and report back with:
- Which check is failing
- The exact error output
- What you tried (all 3 attempts)
- Your hypothesis for why it's still failing

Do NOT report success if any verification check is failing.

## Report Format

When done, report:
- What you implemented
- What you tested and verification gate results (all checks)
- Files changed
- Any concerns
```

**When NOT to use subagents:**
- Tasks that require back-and-forth with the user (clarification, approval)
- Tasks where you need to see the result before deciding next steps
- Very small changes (1-2 line edits) where the overhead isn't worth it

**Note on test types:** Unit tests are preferred when possible. For UI/visual bugs where e2e tests are flaky or unreliable, document that manual testing will be used in Step 7.

### Step 7: Verify Before Completion

**REQUIRED:** Invoke `superpowers:verification-before-completion` skill, or dispatch a Bash subagent to run verification.

**Automated verification:**
Run ALL commands from the project's `.claude/CLAUDE.md` → "Verification Commands" section. These mirror CI exactly and include tests, type checking, linting, and any project-specific checks. Every command must pass.

**E2E tests (REQUIRED if they exist):**
If the project has E2E tests:
1. Start required servers (e.g., `langgraph dev`, `npm run dev`)
2. Run E2E test suite (e.g., `pytest tests/*_e2e.py -v -s`)
3. Wait for all E2E tests to pass before creating PR
4. Stop servers after tests complete

**Chat/agent backend changes:**
When modifying agent behavior (system prompt, tool routing, fallback logic, tools), write E2E tests that verify the agent makes the right tool calls with the right arguments. See the project's `testing-langgraph-backend` skill if available.

**Manual verification (for UI/visual bugs):**
If the bug is visual or e2e tests are unreliable:
1. Start required servers locally (backend + frontend)
2. Reproduce the original bug scenario
3. Verify the fix works
4. Document what was tested in the PR description

**Local deploy for user manual testing:**
For UI features, new pages, or any user-facing changes — after creating the PR and running code review, offer to deploy locally so the user can manual test:
1. Ensure required services are running (e.g., `supabase status`)
2. Copy `.env.local` from main repo to worktree if missing
3. Start the dev server in the worktree: `npm run dev` (run in background)
4. Tell the user the URL (e.g., `http://localhost:3000`) and what to test
5. Wait for user feedback before marking as "In Review"
6. Stop the dev server after user confirms testing is complete

### Step 8: Create Pull Request

Push branch and create PR:

```bash
git push -u origin <branch-name>

gh pr create --title "<PROJ>-<number>: <ticket-title>" --body "$(cat <<'EOF'
## Summary
<2-3 bullets from the design doc>

## Test Plan
- [ ] <verification steps from TDD>

## Linear
<PROJ>-<number>

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Capture the PR URL from output.

### Step 9: Code Review

**REQUIRED:** Invoke `superpowers:requesting-code-review` skill OR use the `superpowers:code-reviewer` agent.

After creating the PR, run a code review before checking CI. This catches logic errors, security issues, missing edge cases, and style problems early — before CI runs and before marking as "In Review".

**How to run the review:**
- Use the Task tool with `subagent_type: "superpowers:code-reviewer"` to spawn a review agent
- Provide the PR number, worktree path, and a summary of what was changed
- The reviewer will read the diff and report issues categorized as Critical / Important / Suggestion

**After review:**
- **Critical issues** — must fix before proceeding. Push fixes, re-run review if needed.
- **Important issues** — should fix. Push fixes.
- **Suggestions** — nice to have. Fix if quick, otherwise note for follow-up.

Present the review findings to the user for their own review before proceeding. Do NOT skip ahead — the user should see the review results and approve before moving to CI.

### Step 10: Check CI

After code review is addressed, verify CI checks pass before marking as In Review:

```bash
gh pr checks <pr-number> --watch
```

- If checks **pass**: proceed to Step 11
- If checks **fail**: read the failure logs with `gh run view <run-id> --log-failed`, fix the issue, push, and re-check
- Don't leave a PR in "In Review" with failing CI — fix it first

```bash
# View failure details
gh run view <run-id> --repo <owner/repo> --log-failed
```

### Step 11: Local Deploy for Manual Testing

**When:** The ticket involves UI features, new pages, or user-facing changes.
**Skip when:** Backend-only changes, type-only changes, or no visual component.

1. Ensure required services are running (e.g., `supabase status`)
2. Copy `.env.local` from main repo to worktree if missing
3. Start the dev server in the worktree (`npm run dev`, run in background)
4. Tell the user the URL and what to test (specific flows from acceptance criteria)
5. Wait for user feedback before proceeding
6. Fix any issues found during manual testing
7. Stop the dev server after user confirms

### Step 12: Update Linear to In Review

```
mcp__linear-server__update_issue with:
- id: "<ticket-id>"
- state: "In Review"
- description: append PR link to existing description
```

Report completion with PR URL.

## Quick Reference

| Step | Action | Skill/Tool |
|------|--------|------------|
| 1 | Fetch ticket | `mcp__linear-server__get_issue` |
| 2 | Mark in progress | `mcp__linear-server__update_issue` |
| 3 | Create worktree | `superpowers:using-git-worktrees` |
| 4 | Design Pass (conditional) | If ticket has Verification + Snapshot → `plan-review-eng` only. Else `superpowers:brainstorming` then `plan-review-eng`. |
| 4.5 | Snapshot Freshness Check (Path A) | Probes from `freshness-check.md`. On failure: Rescue Scout writes `<worktree>/SNAPSHOT.md`. |
| 4.7 | UI Prototype Check (if substantial UI) | Throwaway prototype with real data → screenshot desktop+mobile → user signs off on the look before TDD |
| 5 | Create task list | `TaskCreate` + `TaskUpdate` for dependencies |
| 6 | Implement | Subagents (`Task` tool, `general-purpose`) with TDD |
| 7 | Verify (unit + E2E + manual) | Subagent (`Bash`) or `superpowers:verification-before-completion` |
| 8 | Create PR | `gh pr create` |
| 9 | Code review | Project `scaled-code-review` skill (if exists) OR `superpowers:code-reviewer` agent |
| 10 | Check CI | `gh pr checks --watch` → fix failures if any |
| 11 | Local deploy (if UI) | `npm run dev` in worktree → user manual tests → wait for feedback |
| 12 | Update Linear | `mcp__linear-server__update_issue` → In Review |
| 13 | Merge, Deploy & Cleanup | Project `land-and-deploy` skill (if exists) OR `gh pr merge --squash` → deploy verify → canary → Linear Done → worktree remove → pull main |

## Common Mistakes

### Skipping brainstorming when the ticket is missing Verification or Implementation Snapshot
- **Problem:** Jumps into implementation without understanding requirements; the ticket alone doesn't carry enough context
- **Fix:** Brainstorm whenever the ticket is missing the new sections (Path B). Only skip brainstorming when the ticket has both Verification AND Implementation Snapshot — those sections are what justify the skip.

### Trusting a stale Implementation Snapshot
- **Problem:** Snapshot listed file paths or symbols that have since moved or been renamed; agent edits the wrong file or reinvents a helper that's been refactored
- **Fix:** Always run the Step 4.5 freshness check on rich tickets. If any probe fails, spawn the Rescue Scout — don't paper over a broken anchor.

### Forgetting to mark ticket In Progress
- **Problem:** Team doesn't know work has started
- **Fix:** Mark In Progress immediately after fetching

### Working in main directory instead of worktree
- **Problem:** Pollutes main with in-progress work
- **Fix:** Always create worktree before making changes

### Skipping task list before implementation
- **Problem:** No visibility into progress, user can't see what's being worked on
- **Fix:** Always create tasks from the design BEFORE writing any code. Update status as you work.

### Implementing tasks sequentially instead of with subagents
- **Problem:** Doing each task yourself blocks the main context and is slower
- **Fix:** Dispatch independent implementation tasks to subagents in parallel. Use `Task` tool with `subagent_type: "general-purpose"` and include full context (worktree path, files to modify, acceptance criteria).

### Skipping TDD for "urgent" tickets
- **Problem:** Untested code ships with bugs
- **Fix:** TDD is faster than debugging in production

### Relying only on e2e tests for UI bugs
- **Problem:** E2e tests can be flaky due to timing, backend connectivity, etc.
- **Fix:** Always do manual verification for visual/UI bugs - start the servers and test it yourself

### Skipping manual testing because "tests pass"
- **Problem:** Tests may not cover the exact user scenario
- **Fix:** For UI bugs, reproduce the original issue and verify it's fixed

### Skipping E2E tests before merging
- **Problem:** Unit tests pass but integration/agent behavior may be broken
- **Fix:** Always run E2E tests before creating PR - start the server and run the full E2E suite

### Modifying chat/agent behavior without writing E2E tests
- **Problem:** System prompt, tool routing, or fallback changes break agent behavior in ways unit tests can't catch
- **Fix:** Write E2E tests that verify the agent calls the right tools with the right arguments. Run them against the dev server before creating the PR.

### Skipping code review before CI
- **Problem:** Issues found after CI passes, requiring another push/CI cycle
- **Fix:** Always run the `superpowers:code-reviewer` agent after creating the PR. Fix Critical/Important issues before checking CI. Present findings to user for their review.

### Marking PR as "In Review" without checking CI
- **Problem:** PR has failing CI, reviewer wastes time reviewing broken code
- **Fix:** Always run `gh pr checks --watch` after pushing. Fix failures before marking In Review.

### Working on multiple independent tickets sequentially
- **Problem:** 3 independent tickets take 3x as long when done one-by-one
- **Fix:** Use a team — spawn parallel agents, each with their own worktree. The lead coordinates and collects PRs.

### Using a team for tightly coupled sequential work
- **Problem:** Agents block each other waiting for dependencies, adding coordination overhead with no parallelism benefit
- **Fix:** Only use teams when work is genuinely independent. Sequential dependencies = single-agent workflow.

## Red Flags

- "This is simple, I don't need to brainstorm"
- "Let me just make a quick fix in main"
- "I'll write tests after"
- "I'll create the task list later" (create it BEFORE implementation, not after)
- "The ticket is clear enough"
- "I can figure out the acceptance criteria myself"
- "Unit tests pass, E2E tests can wait"
- "The code looks fine, I don't need a review"
- "I'll just build the real UI — a prototype is a waste" (for substantial new UI, prototype + get look sign-off FIRST; wrong-look rebuilds cost far more)
- "CI will probably pass, I'll mark it In Review now"
- "I'll do these 3 tickets one at a time" (if they're independent, use a team)
- "I'll implement each task myself" (dispatch to subagents for parallelism)
- "This cross-repo ticket is too complex for a team" (it's exactly when teams help most)
- "The PR is merged, we're done" (still need: Linear → Done, worktree cleanup, pull main)

**All of these mean: Follow the workflow. No shortcuts.**

### Step 13: Merge, Deploy & Cleanup

**Trigger:** User says "merge", "merge the PR", or "ship it". Can also be invoked directly mid-conversation for any open PR.

**This is the complete end-of-ticket ceremony. Execute all steps in order — don't skip any.**

**Project override:** If the project has a `land-and-deploy` skill, invoke it instead of following the steps below. The project skill handles deploy monitoring and canary verification specific to that project's infrastructure.

1. **Confirm PR number** with the user if ambiguous (multiple PRs open)

2. **Verify CI is green:**
   ```bash
   gh pr checks <pr-number>
   ```
   If checks are failing, fix first — do NOT merge with red CI.

3. **Merge the PR:**
   ```bash
   gh pr merge <pr-number> --squash --delete-branch
   ```

4. **Monitor deploy** (if project has deploy infrastructure):
   - Wait for deployment to complete (check GitHub deployment status or platform CLI)
   - Verify deployment succeeded before proceeding

5. **Canary verification** (if project has a `canary` skill):
   - Invoke the project's `canary` skill to verify production health
   - If canary reports degradation, alert user and offer revert
   - If healthy, proceed to cleanup

6. **Stop any running servers** started during verification (dev servers, Supabase, etc.)

7. **Clean up worktree:**
   ```bash
   git worktree remove <worktree-path> --force
   ```

8. **Return to main and pull latest:**
   ```bash
   cd <main-repo-path>
   git checkout main
   git pull origin main
   ```

9. **Update Linear to Done:**
   ```
   mcp__linear-server__get_issue with id: "<ticket-id>"
   mcp__linear-server__update_issue with:
   - id: "<ticket-id>"
   - state: "Done"
   ```
   Preserve existing labels (Bug/Feature/Improvement).

10. **Report completion:** Confirm to user: PR merged, deploy verified, Linear updated, worktree cleaned.

**Don't leave worktrees hanging** — they consume disk space and cause confusion in future sessions.
