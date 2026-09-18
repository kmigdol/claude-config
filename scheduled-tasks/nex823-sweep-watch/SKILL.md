---
name: nex823-sweep-watch
description: Daily read of the NEX-823 Creators ASIN sweep after the 10:00 UTC pipeline run: asserts no row was charged during an Amazon block, tracks remediation progress, and says when the --apply step is unblocked. Report-only; never writes to production or moves the ticket.
---

Daily verification read for Linear ticket **NEX-823** (nextbest). **REPORT ONLY.** You must not write to the production database, must not run any pipeline stage with `--apply`, and must not change the ticket's state. Repo: `/Users/kayleigh/dev/nextbest`. Linear team `Nextbest`.

## Why this task exists

NEX-823 fixed the Creators ASIN leg attaching a *sibling SKU's* Amazon listing to a product, and added a re-runnable `verify-creators-asins` sweep that repairs already-stored ASINs. The sweep runs inside the daily Prefect `daily-pipeline` at 10:00 UTC, capped at 60 rows/day.

On its **first** production run (2026-09-17) it misbehaved: Amazon anti-bot-blocked the session after 6 reads, and all 54 blocked rows were charged an `asin_dp_probe_attempts`. Three such days retire a row permanently. Root cause: the circuit breaker's "canary" read went through a per-run ASIN cache and so never actually contacted Amazon. Fixed in PRs #766 and #767 (merged `70dfa86`, `0c559d4`). The 54 counters were reset by hand.

**This task confirms the fix holds in production, every day, and reports remediation progress.** The ticket's last open acceptance criterion (AC 4) is that the stored rows actually get swept.

## The read — run these against PRODUCTION, read-only

Production DSN lives in gitignored `/Users/kayleigh/dev/nextbest/pipeline/.env.prod` (`DATABASE_URL=`). SELECT only; never echo the credential.

```sql
select
  count(*) filter (where coalesce((dossier_json->>'asin_dp_probe_attempts')::int,0) > 0)         as charged_rows,
  count(*) filter (where dossier_json ? 'asin_dp_verified_at')                                   as verified_total,
  count(*) filter (where (dossier_json->>'asin_dp_verified_at')::timestamptz > now() - interval '24 hours') as verified_last_24h,
  count(*) filter (where (dossier_json->>'asin_dp_disproved_at')::timestamptz > now() - interval '24 hours') as disproved_last_24h,
  count(*) filter (where dossier_json @> '{"asin_source":"creators-search"}'
                     and dossier_json->>'amazon_asin' is not null)                               as creators_asin_remaining
from taxonomy_proposals
where status = 'pending' and proposal_type = 'new_product';
```

Also confirm the ticket's own post-merge check still holds (expect **0**):

```sql
select count(*) from taxonomy_proposals
where status='pending' and dossier_json->>'amazon_asin'
      in ('B0CVL46L26','B00EYOHJZ2','B0FDK4B3JD','B004JKNYL4');
```

If any row was disproved in the last 24h, list them (id, canonical_full_name, `creators_dp_recheck->>'observed_title'`, `asin_reason`) so a human can sanity-check what the sweep deleted.

## How to judge it

- **`charged_rows` must be 0. This is the pass/fail.** Non-zero means rows are being charged again — either the breaker is still not detecting a block, or genuinely dead listings are being charged (which is correct behaviour). Distinguish them: dead-listing charges come with `creators_dp_recheck.outcome = 'dp_unobserved'` on a run that *also* verified rows; a block-charge pattern is many charged rows and few or zero verified in the same window. Say which one you think it is, with the numbers.
- **`verified_last_24h` > 0 means Amazon is serving us** — that is the signal the `--apply` step is unblocked (see below).
- **`verified_last_24h` = 0 for several consecutive days** means the sweep is making no progress: either Amazon is blocking every run (expected to show as a "stopped blocked" WARNING, nothing charged) or the sweep is not running at all. Check whether the daily pipeline ran: Prefect flow runs, per `docs/runbooks/nex-390-prefect-cron-cutover.md` § "Reading the Prefect server directly" (credential from `railway variables --service prefect-worker --environment production --kv`, key `PREFECT_API_AUTH_STRING`; server `https://prefect-server-production-013d.up.railway.app/api`).
- **`creators_asin_remaining` should trend DOWN** as rows get verified or repaired. It also grows as the daily research lane adds new rows, so read the direction over several days, not one number.

## What to post

Post ONE comment on **NEX-823** (Linear), short, with the numbers in a small table plus a one-line verdict: `PASS — no rows charged, N verified in 24h` or `FAIL — N rows charged` with your read of which cause. Include the disproved-row list when there is one.

🚨 **Two Linear MCP servers exist and they fail independently.** `mcp__linear-server__*` is the one that keeps losing auth; the other is UUID-named `mcp__5afa51ff-6015-498e-9e18-a1d1d62866c2__*` with the same tools. The string "linear" appears NOWHERE in the second one's names, so searching "linear" finds nothing and it looks like Linear is down. Before concluding that, run `ToolSearch` with the bare verbs: `save_comment get_issue list_issues`, and use whichever prefix comes back.

## Escalate, don't investigate

If the verdict is FAIL, or if `verified_last_24h` has been 0 for 3+ consecutive days, post the comment and then `spawn_task` a self-contained session to investigate (include the numbers you gathered, the ticket id, and the constraint: report-only on Linear state, no `--apply`). Do not debug it inside this run, and do not create a worktree or edit code here.

## When Amazon is serving us again — say so, don't act

AC 4 needs a human-supervised sequence that this task must NOT perform:
1. `verify-creators-asins --dry-run --limit 60`, with every would-null row hand-labelled;
2. the two-judge-run agreement rate recorded (still unmeasured);
3. `--apply` **on Railway, not locally**.

When `verified_last_24h` > 0 (Amazon is serving), end your reply with one line: "Amazon is serving /dp reads again — the AC-4 dry-run + apply is unblocked; it needs Kayleigh." Do not run it.

## Retiring this task

This is time-boxed to NEX-823. If the ticket is **Done**, or AC 4 is recorded as met in its comments, say so in your reply and recommend deleting this scheduled task (`nex823-sweep-watch`) rather than continuing to post. Do not delete it yourself.