---
name: starting-linear-ticket
description: Use when starting work on a Linear ticket - full workflow from fetch to PR creation including worktree setup, brainstorming, TDD implementation, and Linear status updates
---

# Starting Work on a Linear Ticket

## Overview

Complete end-to-end workflow for Linear tickets: fetch → in progress → worktree → brainstorm → task list → TDD → verify → PR → code review → CI → in review.

**Announce at start:** "I'm using the starting-linear-ticket skill to set up for this ticket."

## Required Input

User provides ticket identifier (e.g., "NEX-63", "start NEX-63", or just the number if context is clear).

## When to Use a Team

Before starting the workflow, evaluate whether this work should use a **team of parallel agents**. Use a team when:

### Use a Team When

- **Multiple independent tickets** — User asks to work on 2+ tickets at once (e.g., "start NEX-140, NEX-141, and NEX-142"). Each agent gets its own worktree and runs the full workflow independently.
- **Cross-repo changes** — A single ticket requires changes across multiple repos (e.g., dagster pipeline + backend tools + frontend UI). Each agent works in a different repo/worktree.
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
- `nex-140-agent` — for ticket-based agents
- `frontend-agent` / `backend-agent` / `dagster-agent` — for repo-based agents

### Example: Multiple Tickets

```
User: "Start NEX-140, NEX-141, and NEX-142"

Lead:
  1. Fetch all 3 tickets from Linear
  2. Verify they're independent (no blocking dependencies)
  3. Mark all 3 as "In Progress"
  4. TeamCreate → "nex-batch"
  5. Spawn 3 agents, each with full ticket context
  6. Each agent: worktree → brainstorm → TDD → verify → PR → code review
  7. Lead collects PRs, updates Linear to "In Review"
```

### Example: Cross-Repo Ticket

```
User: "Start NEX-150" (requires dagster + backend + frontend changes)

Lead:
  1. Fetch ticket, brainstorm overall design
  2. Identify which changes go to which repo
  3. TeamCreate → "nex-150"
  4. Spawn agents per repo with their slice of the design
  5. Define task dependencies (e.g., backend blocked by dagster schema)
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
    brainstorm [label="4. Brainstorm design", shape=box];
    todos [label="5. Create task list", shape=box];
    tdd [label="6. Implement with TDD", shape=box];
    verify [label="7. Verify (tests + manual)", shape=box];
    pr [label="8. Create PR", shape=box];
    codereview [label="9. Code review", shape=box];
    ci [label="10. Check CI", shape=box];
    review [label="11. Update Linear\nto In Review", shape=box];

    fetch -> progress -> worktree -> brainstorm -> todos -> tdd -> verify -> pr -> codereview -> ci -> review;
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
- Feature: `feature/nex-<number>-<slug>`
- Bug: `fix/nex-<number>-<slug>`
- Improvement: `improve/nex-<number>-<slug>`

Where `<slug>` is kebab-case from ticket title.

### Step 4: Brainstorm Design

**REQUIRED:** Invoke `superpowers:brainstorming` skill.

Provide context from the ticket:
- Ticket requirements and acceptance criteria
- Current codebase state (explore relevant files)
- Any constraints from linked issues

Brainstorming will:
- Ask clarifying questions one at a time
- Propose 2-3 approaches with trade-offs
- Present design incrementally for validation
- Write design doc to `docs/plans/YYYY-MM-DD-<topic>-design.md`

### Step 5: Create Task List

**REQUIRED:** Before writing any code, create a `TaskCreate` todo list that breaks the design into implementation tasks.

Based on the design from brainstorming, create tasks for:
- Each piece of functionality to implement (API endpoints, components, pages, etc.)
- A verification task (run full test suite + TypeScript + build)
- A PR creation task

Set up dependencies with `TaskUpdate` (e.g., verification blocked by implementation tasks, PR blocked by verification).

Update task status as you work: `in_progress` when starting, `completed` when done. This gives the user visibility into progress.

### Step 6: Implement with TDD

**REQUIRED:** Invoke `superpowers:test-driven-development` skill.

Follow the design from brainstorming. For each piece of functionality:
1. RED - Write failing test
2. GREEN - Minimal code to pass
3. REFACTOR - Clean up

**Note on test types:** Unit tests are preferred when possible. For UI/visual bugs where e2e tests are flaky or unreliable, document that manual testing will be used in Step 7.

### Step 7: Verify Before Completion

**REQUIRED:** Invoke `superpowers:verification-before-completion` skill.

**Automated verification:**
- Run all tests and verify everything passes
- TypeScript compilation: `npx tsc --noEmit`
- Build verification: `npm run build`

**E2E tests (REQUIRED if they exist):**
If the project has E2E tests:
1. Start required servers (e.g., `langgraph dev`, `npm run dev`)
2. Run E2E test suite (e.g., `pytest tests/*_e2e.py -v -s`)
3. Wait for all E2E tests to pass before creating PR
4. Stop servers after tests complete

**Manual verification (for UI/visual bugs):**
If the bug is visual or e2e tests are unreliable:
1. Start required servers locally (backend + frontend)
2. Reproduce the original bug scenario
3. Verify the fix works
4. Document what was tested in the PR description

### Step 8: Create Pull Request

Push branch and create PR:

```bash
git push -u origin <branch-name>

gh pr create --title "NEX-<number>: <ticket-title>" --body "$(cat <<'EOF'
## Summary
<2-3 bullets from the design doc>

## Test Plan
- [ ] <verification steps from TDD>

## Linear
NEX-<number>

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

### Step 11: Update Linear to In Review

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
| 4 | Design | `superpowers:brainstorming` |
| 5 | Create task list | `TaskCreate` + `TaskUpdate` for dependencies |
| 6 | Implement | `superpowers:test-driven-development` |
| 7 | Verify (unit + E2E + manual) | `superpowers:verification-before-completion` + E2E tests + local servers |
| 8 | Create PR | `gh pr create` |
| 9 | Code review | `superpowers:code-reviewer` agent → fix Critical/Important issues → present to user |
| 10 | Check CI | `gh pr checks --watch` → fix failures if any |
| 11 | Update Linear | `mcp__linear-server__update_issue` → In Review |

## Common Mistakes

### Skipping brainstorming for "simple" tickets
- **Problem:** Jumps into implementation without understanding requirements
- **Fix:** Always brainstorm. Even simple tickets benefit from clarifying questions.

### Forgetting to mark ticket In Progress
- **Problem:** Team doesn't know work has started
- **Fix:** Mark In Progress immediately after fetching

### Working in main directory instead of worktree
- **Problem:** Pollutes main with in-progress work
- **Fix:** Always create worktree before making changes

### Skipping task list before implementation
- **Problem:** No visibility into progress, user can't see what's being worked on
- **Fix:** Always create tasks from the design BEFORE writing any code. Update status as you work.

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
- "CI will probably pass, I'll mark it In Review now"
- "I'll do these 3 tickets one at a time" (if they're independent, use a team)
- "This cross-repo ticket is too complex for a team" (it's exactly when teams help most)

**All of these mean: Follow the workflow. No shortcuts.**

## After PR Merged

**REQUIRED:** Complete cleanup when user says "merge" or PR is merged:

1. **Merge the PR** (if not already merged):
   ```bash
   gh pr merge <pr-number> --squash --delete-branch
   ```

2. **Stop any running servers** started during verification

3. **Clean up worktree:**
   ```bash
   git worktree remove <worktree-path> --force
   ```
   Or invoke `superpowers:finishing-a-development-branch` skill.

4. **Update Linear to Done:**
   ```
   mcp__linear-server__update_issue with:
   - id: "<ticket-id>"
   - state: "Done"
   ```

**Don't leave worktrees hanging** - they consume disk space and can cause confusion.
