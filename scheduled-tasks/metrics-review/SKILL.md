---
name: metrics-review
description: Daily read of the named metric on every Linear ticket in Monitoring; posts the numbers as a comment, then walks the decisions one at a time. Never moves a ticket unprompted — only on Kayleigh's explicit instruction.
---

Daily metrics review for the nextbest project. **Report only — you must never change a ticket's state.**

Repo: `/Users/kayleigh/dev/nextbest`. Linear team: `Nextbest` (key NEX). PostHog project 349365 (org nextbest).

## 🚨 Finish the whole review before acting on any of it

**Post the per-ticket comment for EVERY ticket in Monitoring before starting work on any individual ticket.** The review is a single deliverable; it is not done until every ticket has its comment.

This holds even when the user redirects mid-review — a request to go fix or ship something on one ticket is **not** permission to abandon the other reads. Finish the comments first (they take seconds each), then pick up the work. If the user's request is genuinely urgent, say that you are posting the remaining comments first and then proceeding.

Why: the review's value is the *complete* picture — which tickets are stuck, which are unreadable, which nobody has actioned. Half a review posted, plus a day of work on one ticket, leaves the other tickets with no record for that day and no way to tell later whether they were read at all. This has already happened once (2026-08-10: the review was abandoned at ticket 5 of 10 to work NEX-552, and the remaining comments were only posted after the user asked).

## What to do

1. **Find the tickets.** `mcp__linear-server__list_issues` with `team: "Nextbest"`, `state: "Monitoring"`. If none, post nothing anywhere and reply with one line: "No tickets in Monitoring." Then stop.

2. **For each ticket**, `mcp__linear-server__get_issue` and find the metric it named — look for a "Post-ship" or "Analytics" acceptance criterion, or a Measured-impact section. It usually names a specific PostHog event and a denominator, e.g. "Google-organic card+hero clicks per `alternatives_section_viewed`".

   If the ticket names **no** metric, comment once saying it's in Monitoring without a named metric and should either get one or move to Done, then move on. Do not invent a metric for it.

   **If the ticket carries an explicit exit checklist** — a "Post-Merge Verification", "Monitoring Exit Checklist", or similar section listing concrete queries/commands — **run every item in it and report each result separately.** That checklist is the ticket author's own definition of done; it outranks your judgement about which single observable matters. A checklist item you skipped is reported as unread, and the ticket cannot be recommended for close while any item is unread.

3. **Read the metric from wherever it actually lives.** Most Monitoring tickets here are pipeline/infra work, and their observables are **not** PostHog events. Pick the source from the ticket:
   - **PostHog** — traffic, funnel and CTR metrics. Use the PostHog MCP tools (`mcp__a1b28c81-1281-4eee-a940-e5db946cc335__*`; find them with ToolSearch, query "posthog query insight").
   - **Supabase MCP (`execute_sql`)** — counts, audit queries, queue depths, `pipeline_stage_runs`. This is the most common case.
   - **Production HTTP** — `curl` for 200/404, rendered copy, `search-index.json` membership.
   - **Railway logs** — `railway logs --service <name> --environment production`. Use this whenever a ticket's observable is "the stage/leg completes without crashing" rather than a number. You CAN read these; report-only means you never move a ticket, not that you skip a command.
     - ⚠️ **Railway retains logs for the LATEST DEPLOY ONLY.** A cron tick and a merge-triggered rebuild each create a new deployment, so an earlier run's logs are gone. Since every push to `main` now rebuilds these services, a same-day merge can wipe the morning cron's logs before you read them. If the latest deployment is not the run you wanted, say the evidence was **lost to a later deploy** — do not report that as clean.
     - Cross-check what you're reading with `railway status --json` → `serviceInstances[].latestDeployment.meta.commitHash` / `.createdAt`.
   - **Google Search Console / CrUX** — readable via `claude-in-chrome` against Kayleigh's logged-in session. Navigate `search.google.com/search-console/performance/search-analytics?resource_id=sc-domain%3Anextbest.one` with `num_of_days=28`, `breakdown=query|page|device`, `page=~%2Fingredients%2F` for a contains-filter, then `get_page_text`. **Do NOT report GSC as needing a human.** ⚠️ Breakdown tables are *sampled* under a page filter — the device rows can cover as little as 17% of the filtered impressions, so quote the unfiltered totals as the headline and the split as indicative.
   - **The self-hosted Prefect server IS reachable** — this is the only way to tell a deploy collision from a clean crash, because NEX-523's detector converts a zombie `RUNNING` into `Crashed` and Sentry shows both identically.
     ```bash
     PA=$(railway variables --service prefect-worker --environment production --json \
          | python3 -c "import json,sys;print(json.load(sys.stdin)['PREFECT_API_AUTH_STRING'])")
     PURL="https://prefect-server-production-013d.up.railway.app/api"   # public twin of the internal URL
     curl -s -u "$PA" -X POST "$PURL/flow_runs/filter" -H 'Content-Type: application/json' \
       -d '{"flow_runs":{"deployment_id":{"any_":["7b9f58d8-6403-47c4-bf61-2144b9402d45"]}},"sort":"START_TIME_DESC","limit":20}'
     curl -s -u "$PA" -X POST "$PURL/work_pools/nextbest-worker/workers/filter" \
       -H 'Content-Type: application/json' -d '{"limit":200}'
     ```
     `7b9f58d8-…` is the `daily-pipeline` deployment. To classify a crash: compare each worker's `created` / `last_heartbeat_time` against the run's `start_time` / `end_time`, then correlate to a `pipeline/**` commit via `git log`. Note this leaves the Railway CLI linked to `production` — say so in the digest.
   - **Genuinely not reachable:** Vercel usage/billing (ISR writes, transformation counts) and Google's Rich Results Test. **Say so plainly and name who has to read it** — never substitute a proxy metric and never imply a pass.

   **Before writing "not reachable / needs a human" about anything, check this list.** Five consecutive reviews deferred the Prefect read as human-only; it took two minutes and it overturned an AC that had been reported as passing. Declaring a metric unreadable is not a neutral non-answer — it defers the work indefinitely.

   **A metric you could not read is reported as "unread", not "flat".** Those are different findings and conflating them fakes a result.

   Rules that matter for PostHog reads:
   - **Always set `filterTestAccounts: true`** — internal traffic is roughly 25% of events and skews everything.
   - Compare a **post-ship window against an equal-length pre-ship window**, using the ticket's own ship date (its `completedAt`, or the merge date in a comment/PR link) as the split.
   - Segment the same way the ticket did. If it said Google-organic-only, filter to that — don't silently widen to all traffic.
   - Report the raw numerator and denominator, not just a percentage. `59/884` is auditable; "6.7%" alone is not.

4. **Post one comment per ticket** with `mcp__linear-server__save_comment`. Keep it compact:
   - Days elapsed since ship, and the two windows compared
   - Numerator/denominator and rate for each window
   - Direction: improved / regressed / flat / not enough data
   - Any **confounder** — another ticket that shipped into the same surface in the same window. Check recently-completed NEX tickets touching the same pages. If one exists, say the read is **unattributable** rather than claiming a result.
   - Your recommendation: keep monitoring / ready to close / looks like a regression

5. **Never move a ticket on your own initiative.** Not to Done, not back to In Progress. A human decides; you supply numbers. This is absolute for the unattended scheduled run.

   **The one exception is an explicit instruction from Kayleigh in a live session** — "close it", "move it back to In Progress". Then move it, and:
   - Post the closing/reopening AC audit **first**, so the reasoning is on the record before the state changes.
   - **Preserve the Bug/Feature/Improvement label** on the update — `labels` replaces the whole set, so pass it back explicitly.
   - **Tick the AC checkboxes in the description** as part of closing, each with its evidence. A ticket closed with six unticked boxes is not auditable later.
   - `Done` only when every AC is met with evidence, or dropped with sign-off on the record. If any AC failed, recommend `In Progress` and say which — do not close over it.

6. **Only after every ticket has a comment**, reply with the digest — and only then take on any work the review surfaced.

## Judgement rules (important)

- **Traffic is too low for statistical significance.** Do not compute or cite p-values or claim a result is "significant". Read slope and funnel health directionally. Say "directional signal", never "proven".
- **Under ~200 denominator events in the post window, say so explicitly and recommend continuing to monitor.** A 3-day read on 40 sessions is noise.
- **A single day is never a baseline.** If the pre-window overlaps a backfill, deploy, or another ship, flag it.
- **Absence of movement is a finding**, not a failure to report. Say "flat" plainly.
- Never describe a metric as improved when the numbers don't show it. If the read is bad news, lead with the bad news.
- **A metric gated on human action is not a metric that elapsed time will move.** If the observable depends on someone working a queue or reading a dashboard, and that hasn't happened, say so and recommend a decision rather than "keep monitoring" — otherwise the ticket reads "flat" forever.
- **Check whether the ticket's observable was revised on the record.** Read the comments, not just the description: an AC may have been formally superseded with sign-off. Judge against the revised one and say which you used.
- **A ticket with unfinished implementation work does not belong in Monitoring.** If ACs are unchecked because work remains (not because a number is pending), say so and recommend moving it back to In Progress.
- **A stage's `last_run_at` is not proof it ran your code.** Dirty-gated stages (`synthesize`, `community_score`, …) skip when no rows changed, so an audit can read clean simply because the stage never re-ran. Check `pipeline_stage_runs.last_run_at` against the ship time before calling an enforcement AC verified.

## Output

### Step 1 — the digest (always)

Reply with a short digest: one line per ticket (identifier, direction, recommendation), then a short section naming only the tickets that need a decision. Note explicitly if you posted no comments and why.

The digest is the whole deliverable for an unattended run. Stop there.

### Step 2 — the walkthrough (whenever Kayleigh is present)

**Do not dump every finding at once.** After the digest, work the tickets that need a decision **one at a time, in urgency order**, and wait for her answer before moving to the next. Lead each with the recap — she will not have the ticket loaded in her head, and a finding without its context is unactionable.

Format for each item:

> ## N of M — NEX-XXX
>
> **Title:** the ticket title
> **Shipped:** date · PR link · label, priority
>
> **Outcome:** what the ticket set out to change, in plain terms — one short paragraph, including the baseline number it named. If the outcome was revised on the record, say so and give the revised one.
>
> **Acceptance criteria, with status:** a table — `#` / AC / ✅ ⚠️ ❌ ⏳ / one-line evidence. Include every AC, not only the interesting ones; the pattern matters (5 of 7 clean reads very differently from 2 of 7).
>
> **Then today's finding** — the numbers, with numerator/denominator.
>
> **Then a recommendation**, and **one explicit question** ending the message.

Rules for the walkthrough:

- **One decision per message.** Never batch two tickets' questions. If she answers one, act on it, then present the next.
- **Order by urgency, not ticket number.** A read window closing tomorrow outranks one due in September.
- **Skip the tickets with nothing to decide.** "Keep monitoring, nothing due until 09-08" belongs in the digest, not as its own turn.
- **Give a recommendation, not a menu.** Say what you'd do and why; offer the alternative in a sentence. Where a call is genuinely hers (an AC being read down, a criterion being rewritten), say that plainly.
- **State plainly when you can't verify something**, and give the manual steps so she can in seconds. Never let "I couldn't reach it" pass as "it's fine".
- **Investigate before escalating.** If a finding has two candidate causes with opposite implications, run the discriminating query and report the answer — don't hand her an open question you could have closed. (2026-08-13: a 7% link-coverage drop looked like silent rot; one query showed 0 stale spans out of 264 and cleared it.)

### Durable formatting note

Prefer tables for anything with more than two dimensions. Bold the number that carries the finding. Lead with bad news when there is bad news.