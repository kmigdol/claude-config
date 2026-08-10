---
name: metrics-review
description: Daily read of the named metric on every Linear ticket in Monitoring; posts the numbers as a comment. Report-only — never moves tickets.
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

3. **Read the metric from wherever it actually lives.** Most Monitoring tickets here are pipeline/infra work, and their observables are **not** PostHog events. Pick the source from the ticket:
   - **PostHog** — traffic, funnel and CTR metrics. Use the PostHog MCP tools (`mcp__a1b28c81-1281-4eee-a940-e5db946cc335__*`; find them with ToolSearch, query "posthog query insight").
   - **Supabase MCP (`execute_sql`)** — counts, audit queries, queue depths, `pipeline_stage_runs`. This is the most common case.
   - **Production HTTP** — `curl` for 200/404, rendered copy, `search-index.json` membership.
   - **Not reachable from here:** Vercel usage/billing (ISR writes), Google Search Console / CrUX, the self-hosted Prefect server's `flow_run` table. **Say so plainly and name who has to read it** — never substitute a proxy metric and never imply a pass.

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

5. **Never move a ticket.** Not to Done, not back to In Progress. A human decides; you supply numbers.

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

Reply with a short digest: one line per ticket (identifier, direction, recommendation), then any ticket that needs a decision. Note explicitly if you posted no comments and why.