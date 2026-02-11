# Global Claude Code Instructions

## Superpowers (Skills)

**🚨 ALWAYS USE SUPERPOWERS - Check for applicable skills BEFORE any action 🚨**

If there's even a 1% chance a skill applies, invoke it with the `Skill` tool. Don't rationalize or skip.

**Common skills**: `brainstorming`, `systematic-debugging`, `test-driven-development`, `writing-plans`, `verification-before-completion`, `requesting-code-review`, `using-git-worktrees`, `finishing-a-development-branch`

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

---

## Investigate Before Proposing Fixes

**Do not propose fixes based on assumptions.** Investigate fully first.

When debugging an issue or error, your investigation MUST include all 4 steps before suggesting any fix:
1. **Reproduce the error** — run the failing command/test and capture the actual output
2. **Read all relevant source files** — don't skim, read the full context of the affected code paths
3. **Check recent git changes** to affected files — `git log --oneline -10 <file>` to understand what changed recently
4. **Propose 2-3 ranked hypotheses with evidence** — each hypothesis must cite specific code/output, not guesses

Do not stop until all 4 steps are done. Do not skip to a fix after step 1.

---

## Verify APIs and Library Versions

**Do not assume API patterns are current.** Libraries change between versions.

Before using any framework or library API:
1. **Check the installed version** (`pip show <package>`, `pnpm list <package>`, etc.)
2. **Verify the API matches that version** — check docs, changelogs, or source code in `node_modules`/site-packages
3. If unsure, **read the actual source** rather than relying on memory of older patterns

This especially applies to: Dagster, LangGraph, assistant-ui, Next.js, and any rapidly-evolving library.

---

## Task Tracking with Linear

**Team**: blairsocial
**Project**: Beta Launch
**Project URL**: https://linear.app/blairsocial/project/beta-launch-ed7a18f92218

### When to Create Tasks

Create a Linear task for non-trivial work: features, bugs, refactors, multi-file changes, or anything taking >5 minutes.

### Creating Tasks

```
mcp__linear-server__create_issue with:
- title: "Task title"
- description: "Task description with context"
- team: "blairsocial"
- project: "Beta Launch"
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
4. Make commits (reference task: "NEX-5: Add feature")
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
- **Cross-repo changes** — A single ticket touching multiple repos (dagster + backend + frontend). Each agent works in its own repo/worktree.
- **Large ticket with separable subtasks** — Independent pieces that don't block each other

**Don't use teams when:**
- Single ticket in a single repo
- Tightly coupled sequential changes (schema → backend → frontend in order)
- Small/quick tickets where coordination overhead exceeds the benefit

The `starting-linear-ticket` skill has full team setup details.

### PR Requirements
- Link to Linear task (NEX-X)
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
