# In-Flight Conflict Check

Probes for Step 1.5. Goal: decide **Clear / Sequencing / Blocked** before marking a ticket In Progress.

Budget ~2 minutes. This is cheap compared to discovering the collision after both branches are built.

---

## 0. Enumerate what is in flight

Linear and the local checkout each miss things the other catches — run both.

```
mcp__linear-server__list_issues with:
- team: "<team-name>"
- state: "In Progress"          # then repeat with "In Review"
- fields: ["id", "title", "status", "gitBranchName", "updatedAt"]
```

```bash
git worktree list
gh pr list --state open --json number,title,headRefName,files \
  --jq '.[] | "\(.number) [\(.headRefName)] \(.title)\n  \([.files[].path] | join(", "))"'
```

A worktree whose branch has no commits still counts — check uncommitted work:

```bash
for wt in $(git worktree list --porcelain | awk '/^worktree /{print $2}'); do
  echo "===== $wt"
  git -C "$wt" diff --name-only origin/main...HEAD   # committed
  git -C "$wt" status --porcelain                     # uncommitted
done
```

Ignore stale worktrees whose ticket is already Done/merged — cross-reference against the Linear list.

---

## 1. File overlap

Write down the files **this** ticket will touch (from its Implementation Snapshot, or from a quick
grep for the symbols it names). Intersect against the in-flight file lists from step 0.

- Same file, different function → usually **Clear**, note it for rebase.
- Same file, same function/component → **Sequencing** at minimum.
- Same *config* file (`CLAUDE.md`, workflow YAML, `package.json`) → **Sequencing**; these conflict
  textually far more often than their size suggests.

## 2. Shared production resource

**The class git cannot see.** Ask: at apply time, do these two tickets write the same thing?

Check for both tickets touching the same —

- **Database table or ledger** the other backfills, scrubs, or repairs
- **Schema object** redefined by `CREATE OR REPLACE` in both (functions especially — two new
  append-only migration files, zero git conflict, last write wins)
- **Cron / scheduled flow**, or a stage inside the daily pipeline
- **Out-of-repo config**: dashboard integrations, platform env vars, feature flags, DNS
- **Long-running prod operation**: a backfill or re-extract already in flight

A ticket that bulk-repairs or backfills a table takes a snapshot; anything merging mid-repair lands
outside it. That is **Sequencing**, always.

## 3. Mechanism change under an in-flight dependent

Ask: **does this ticket change a path something else is already queued to ride through?**

Typical dependents — an in-flight ticket that has
- a migration awaiting auto-apply, when this ticket changes how migrations get applied
- a page awaiting a publish/build gate this ticket rewrites
- a pipeline stage awaiting a deploy path this ticket reroutes

The failure mode is silence: the dependent merges, its step no longer runs, no test fails. If this
ticket's plan contains "gate", "replace", "disable", or "cut over" applied to a shared pipeline,
check every in-flight ticket for something queued in that pipeline. **Sequencing or Blocked.**

## 4. Wide mechanical churn

Does this ticket mass-rename, move, or codemod a directory? Then every open branch eats a rebase
even with zero textual overlap. Cheap to check:

```bash
git -C "$wt" diff --name-only origin/main...HEAD | grep -c '^<dir-being-churned>/'
```

Zero hits across all in-flight branches → **Clear**, proceed. Otherwise land the churn when the
affected branches are merged, or do it first and rebase them immediately.

---

## Reporting the verdict

State all three: **verdict**, **what collides with what**, **what unblocks it**.

> **Sequencing.** Phase 3 (bulk ledger repair) collides with NEX-672, which has an unmerged
> migration that will be auto-applied on merge — the repair snapshot would miss it. Phases 1–2
> (investigation, CI check) are Clear. Unblocked once NEX-672 merges, or by running the repair
> after it.

A bare "no conflicts found" is not a verdict — it does not say which classes were checked.

Never silently downgrade a Sequencing verdict to Clear because the collision seems small. Present it
and let the user decide.
