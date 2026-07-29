---
name: metrics-review
description: Daily read of the named metric on every Linear ticket in Monitoring; posts the numbers as a comment. Report-only — never moves tickets.
---

Daily metrics review for the nextbest project. **Report only — you must never change a ticket's state.**

Repo: `/Users/kayleigh/dev/nextbest`. Linear team: `Nextbest` (key NEX). PostHog project 349365 (org nextbest).

## What to do

1. **Find the tickets.** `mcp__linear-server__list_issues` with `team: "Nextbest"`, `state: "Monitoring"`. If none, post nothing anywhere and reply with one line: "No tickets in Monitoring." Then stop.

2. **For each ticket**, `mcp__linear-server__get_issue` and find the metric it named — look for a "Post-ship" or "Analytics" acceptance criterion, or a Measured-impact section. It usually names a specific PostHog event and a denominator, e.g. "Google-organic card+hero clicks per `alternatives_section_viewed`".

   If the ticket names **no** metric, comment once saying it's in Monitoring without a named metric and should either get one or move to Done, then move on. Do not invent a metric for it.

3. **Read the metric from PostHog.** Use the PostHog MCP tools (`mcp__a1b28c81-1281-4eee-a940-e5db946cc335__*`; find them with ToolSearch, query "posthog query insight"). Rules that matter here:
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

## Judgement rules (important)

- **Traffic is too low for statistical significance.** Do not compute or cite p-values or claim a result is "significant". Read slope and funnel health directionally. Say "directional signal", never "proven".
- **Under ~200 denominator events in the post window, say so explicitly and recommend continuing to monitor.** A 3-day read on 40 sessions is noise.
- **A single day is never a baseline.** If the pre-window overlaps a backfill, deploy, or another ship, flag it.
- **Absence of movement is a finding**, not a failure to report. Say "flat" plainly.
- Never describe a metric as improved when the numbers don't show it. If the read is bad news, lead with the bad news.

## Output

Reply with a short digest: one line per ticket (identifier, direction, recommendation), then any ticket that needs a decision. Note explicitly if you posted no comments and why.