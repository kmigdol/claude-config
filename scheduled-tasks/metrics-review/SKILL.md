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

## 🚨 Spin deeper investigation out into its own session — early

This review **reads and reports**. The moment a finding turns into *work*, stop and hand it off with `spawn_task` rather than doing it inline.

**The bright line.** Bounded checks that close a question you already have are part of the review — run them:

- a SQL query, a `curl`, a `$host` split, a live-vs-expected comparison on a handful of pages
- the discriminating check that separates two candidate causes (see *Investigate before escalating*, below — that rule still stands and this one does not override it)

Open-ended work that *generates* new questions is not part of the review — hand it off:

- reading render internals to decide what a metric should mean
- writing or changing code, creating a worktree, running builds or test suites
- auditing a sample of N pages, or any check whose scope you'd have to choose

**Concrete triggers — any one of these means spin out now, not after one more look:**

1. You are about to create a worktree, edit a file, or run a build/test suite.
2. You've said "let me check one more thing" twice on the same ticket.
3. The finding requires a **design decision** ("what should this number count?") rather than a measurement.
4. You've asked the user two consecutive questions about the same ticket.
5. The next step needs more than ~3 tool calls to reach an answer.

**How to hand off:** `spawn_task` with a self-contained prompt — the evidence you already gathered (tables, numbers, file:line), what to do next, the constraints (report-only on Linear state, don't move the ticket), and any unrelated findings flagged as *separate, do not fold in*. Then post the same evidence as a Linear comment so the ticket carries it, and **return to the walkthrough**.

Why: on 2026-08-17 a single NEX-661 finding (a title over-claiming its dupe count) expanded inside the review into a count-definition debate, a read of the page's render internals, a worktree, and finally a live-SERP audit that invalidated the ticket's whole instrument. All of it was *useful* — and none of it belonged in a metrics review. The walkthrough got to item 1 of 10. The audit became its own session in the end; it should have from the moment it needed a design decision.

A spun-out investigation is not a deferral. It is the same work, in a session that can actually hold it.

## 🚨 What Monitoring is for — effects in production, not correctness

**Monitoring asks one question: did the intended effect actually happen in production?** It does not ask whether the code is correct. Correctness is the PR's job, and it was settled before merge.

The distinction, because it is easy to blur:

| Not this (correctness) | This (effect) |
| -- | -- |
| Does the section render on the right pages? | Did anyone engage with it, and did the funnel move? |
| Do the analytics events fire? | What do the events *say* — did the rate change vs pre-ship? |
| Is the data shaped the way the AC specified? | Did reshaping the data change what users do? |
| Are there N rows violating the constraint? | Did the constraint's *purpose* get served? |

**A ticket's stated observable is often a data property** ("median word count drops 29 → 13", "zero cards over 16 words"). Read it — it is the ticket's own bar — but do not stop there and do not turn the review into a hunt for stragglers. **The 14 rows still over target are not the finding. Whether shorter cards changed behaviour is the finding.** Almost every ticket here names a secondary behavioural metric for exactly this reason; if you only report the data property, you have reported the easy half.

**Verifying a mechanism is in scope only as a precondition for reading its effect.** Confirming links still render before reporting zero clicks is correct — it separates "nobody clicked" from "nothing was there to click" (see the zero-count rule below). Confirming links render *as the deliverable* is not.

**When a ticket names no behavioural metric,** say so and recommend it get one or move to Done — do not substitute a correctness audit to fill the gap. A ticket whose only observable is "the code does what it says" did not need Monitoring; that is the signal to close it, not to inspect it harder.

**A stray correctness defect found while reading a metric** gets one line in the comment and, if it matters, a spawned task. It does not become the comment, and it does not hold the ticket in Monitoring — elapsed time will never fix it, so it is not a monitoring question.

## What to do

1. **Find the tickets.** `mcp__linear-server__list_issues` with `team: "Nextbest"`, `state: "Monitoring"`. If none, post nothing anywhere and reply with one line: "No tickets in Monitoring." Then stop.

2. **For each ticket**, `mcp__linear-server__get_issue` and find the metric it named — look for a "Post-ship" or "Analytics" acceptance criterion, or a Measured-impact section. It usually names a specific PostHog event and a denominator, e.g. "Google-organic card+hero clicks per `alternatives_section_viewed`".

   If the ticket names **no** metric, comment once saying it's in Monitoring without a named metric and should either get one or move to Done, then move on. Do not invent a metric for it.

   **If the ticket carries an explicit exit checklist** — a "Post-Merge Verification", "Monitoring Exit Checklist", or similar section listing concrete queries/commands — **run every item in it and report each result separately.** That checklist is the ticket author's own definition of done; it outranks your judgement about which single observable matters. A checklist item you skipped is reported as unread, and the ticket cannot be recommended for close while any item is unread.

### Ticket-specific checks currently armed

Run these IN ADDITION to the ticket's own observables. Each names its own removal condition — **delete the entry when that condition is met**; this list is not meant to accumulate.

#### NEX-734 — is the NEX-668 variant annotation actually being written?

*Armed 2026-08-31. Remove once answered either way.*

C7 (`near_sibling`) is this ticket's load-bearing dedup control, and it works by reading `evidence_json.variant_suggestion`, which the `annotate_pending` pass writes earlier in the same run. On 2026-08-31 a proposal was found that SHOULD carry an annotation and did not — its candidate bucket resolves cleanly to one catalogued product:

```
proposal : "Green Clean Cleansing Balm makeup + SPF melting cleansing"  (Farmacy, cleansing balm)
catalog  : "Green Clean Makeup Removing Cleansing Balm"                 (20 mentions)
both stem to "green clean"; same brand_id; same category
```

Kayleigh confirmed these are two SIZES of one product, i.e. a genuine duplicate that C7 must refuse. The benign explanation is that the proposal is simply newer than the last `annotate_pending`. The alternative — the pass silently skips rows — would mean C7 is blind far more often than it looks, and that blocks re-enabling `AUTO_APPROVE_PRODUCTS_ENABLED`.

**Run (the daily pipeline is 10:00 UTC; this task runs 16:00 UTC, so the annotation should exist):**

```sql
select coalesce((evidence_json->'variant_suggestion')::text, 'NO ANNOTATION') as annotation,
       status
from taxonomy_proposals
where dossier_json->>'canonical_full_name' ilike 'Green Clean%'
  and proposal_type = 'new_product';
```

Then, from the repo, the gate's own view — read-only, applies nothing:

```bash
cd /Users/kayleigh/dev/nextbest/pipeline && \
  railway run --service nextbest --environment production -- \
  uv run python scripts/nex734_revalidate_auto_approve.py
```

**Report:**
- **Annotation present** and the Green Clean row is gone from SWEEP 1 / the qualifier set → C7 is working; say so plainly, and this entry can be removed.
- **Annotation still absent** → a NEX-668 defect. Say so, do NOT recommend re-enabling the flag, and `spawn_task` to investigate `annotate_pending` (it is code work, so it does not belong in the review).
- Also report SWEEP 2 and SWEEP 3 hit counts (bar: 0 each) and the qualifier count.

Note `AUTO_APPROVE_PRODUCTS_ENABLED` is **unset** on production `prefect-worker`, so this ticket's own Outcome metric (the approve-ready queue falling) CANNOT move. Do not report that as "flat" — it is **not running**, which is a different finding. The remaining work is a human pass over the qualifier set (AC 1), then setting the flag.

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
   - **Vercel usage/billing — REACHABLE via `claude-in-chrome`.** ~~Previously listed here as not reachable; that was wrong and it cost real work.~~ Go to `https://vercel.com/kayleighs-projects-edc9a973/~/usage`, scroll to **Consumption Breakdown**, and read the per-product rows (ISR Writes, ISR Reads, Image Optimization Transformation, Build CPU Minutes, Observability Events). **Each row is clickable** and drills into a per-day chart — use that to answer "did it spike after the deploy", which the cycle total cannot. Read counts and hours, not dollars.
     - ⚠️ The usage page is script-heavy and `screenshot`/`get_page_text` frequently time out on a tab that has already navigated a few times. **Open a fresh tab** (`tabs_create_mcp`) and load it there — that works reliably. `javascript_tool` is blocked on this origin.
   - **Google's Rich Results Test — REACHABLE via `claude-in-chrome`.** Navigate to `https://search.google.com/test/rich-results?url=<urlencoded>`; it auto-runs and redirects to a `/result?id=…` page in ~10s. Read the "N valid items detected" banner, then click into each type (Breadcrumbs, Carousels, …) for per-item errors and warnings.
   - **Supabase org usage page — REACHABLE, but the tab must be FOREGROUNDED.** `https://supabase.com/dashboard/org/<org>/usage`. Driven as a background tab the dashboard defers rendering entirely: `document.visibilityState === "hidden"`, `body.innerText.length === 0`, `get_page_text` returns "No text content found", and `read_page` returns an empty accessibility tree — which reads exactly like an outage or an auth wall, and is neither. **Fix: take a `computer` screenshot of the tab first.** That forces the paint; wait ~5s for the data to load past the skeletons, then `get_page_text` returns the whole page. Measured 2026-08-24 (NEX-681): first attempt reported "blocked", the screenshot trick then returned the full reading in one call. GSC does NOT behave this way, so a failure here is not evidence about any other dashboard. Read the "Egress / Used in period / Overage in period" block; note the page shows only the CURRENT cycle.
   - **Mediavine publisher portal — REACHABLE via `claude-in-chrome`.** `https://publishers.mediavine.com/` against Kayleigh's logged-in session; no credential entry needed. The Home card carries a **Revenue / RPM / Traffic** toggle: Revenue gives Yesterday / Month-to-date / Last month, RPM gives per-session and per-page, Traffic gives sessions and pageviews. That is the entire ad-revenue side of the NEX-759 ledger. First read 2026-08-31 — earlier the same day it had been reported "unread, no documented path", which left a keep/adjust/pull decision blocked on nothing. Note `/tasks` renders an "Urgent Tasks" heading with an empty body under automation even when the sidebar badges a count; read the task list by hand.
   - **⚠️ `vercel logs` CANNOT answer "zero errors over the last N days".** It returns only the most recent **100 entries** and silently ignores `--since`. Asked for four days on 2026-08-31 it returned a **three-minute** window (11:41:51 → 11:44:53) — and a grep over that finding nothing looks exactly like a clean week. This is "exit code 0 does not mean the check ran" in a new costume. Before reporting any absence-of-errors AC as met, check the span the command actually returned (read the oldest timestamp in its output); when the window matters, use Vercel dashboard observability with a real time filter, or Sentry.
   - **Genuinely not reachable:** nothing else currently known. If you hit something, say so plainly, name who has to read it, and **add it here** — never substitute a proxy metric and never imply a pass.

   **Before writing "not reachable / needs a human" about anything, check this list — and then try anyway.** This file's own "not reachable" list has now been wrong twice. Five consecutive reviews deferred the Prefect read as human-only; it took two minutes and overturned an AC reported as passing. On 2026-08-17 the review deferred NEX-667's AC 3 and AC 6 as human-only **because this file said they were** — Kayleigh pushed back, and both were closed inside five minutes (Vercel: 649 transformations / $0.04, no post-deploy spike; RRT: 2 valid items, zero errors). Declaring a metric unreadable is not a neutral non-answer — it defers the work indefinitely, and a stale entry on this list launders that deferral as a fact.

   **The rule: attempt the read, then report what happened.** "I tried X and hit Y" is a finding. "It needs a human" without an attempt is not.

   **A metric you could not read is reported as "unread", not "flat".** Those are different findings and conflating them fakes a result.

   Rules that matter for PostHog reads:
   - **Always set `filterTestAccounts: true`** — internal traffic is roughly 25% of events and skews everything.
   - 🚨 **`execute-sql` does NOT apply `filterTestAccounts`.** That flag is honoured by the `query-*` tools only. Any raw SQL over `events` is unfiltered by default and will silently include internal traffic. Filter inline: `properties.$host = 'www.nextbest.one'`, and check `person.properties.email` before believing a small count.
   - 🚨 **Break every event count down by `$host` BEFORE reporting it. Never report a bare total.** Vercel preview hosts (`nextbest-*.vercel.app`, `nextbest-git-*.vercel.app`) carry the developer's own post-deploy verification clicks, and for a newly-shipped feature they are frequently *most* of the events. Report production and preview as separate columns, and read the metric off production only.

     The query shape:

     ```sql
     SELECT toDate(timestamp) AS day, properties.$host AS host, properties.<surface_prop> AS surface, count() AS n
     FROM events
     WHERE event = '<event>' AND timestamp >= now() - INTERVAL 21 DAY
     GROUP BY day, host, surface ORDER BY day DESC
     ```

     This is not hypothetical and it cuts both ways — on 2026-08-17 it changed the finding on four tickets in one review:
     - **NEX-650 / 663 / 672**: `summary_entity_link_clicked` showed 20 events, which read as a working feature. Split by host: 13 were Vercel previews, and the 7 "production" ones were 2 people in 3 sessions inside 27 minutes, one of them Kayleigh's own logged-in account. **Real organic clicks: zero.** Reported bare, that number would have read as a ~2.7% link CTR.
     - **NEX-487**: the reverse error. A bare "4 impressions, 1 click" read as broken instrumentation. Split by host and divided by *eligible* pageviews, it was 1 impression per 8 eligible views — right on the ~15% below-fold benchmark. The analytics were fine; the exposure was 4.2%.

   - **When an event count is near zero, find its real denominator before calling it a failure.** Not all pageviews — the ones that could possibly have fired it. A section that only renders on 64 of 799 products has a denominator of "views of those 64", not "all product views". Getting this wrong turns a coverage problem into a false instrumentation bug, or hides one.
   - **A zero-count event needs one discriminating check before you report it as an absence of clicks.** Confirm the feature still renders in production (`curl | grep -c 'data-testid=…'`) and that sibling events are flowing in the same window. Rendering + healthy sibling events = genuine absence; missing markup or a site-wide event gap = a regression, which is a completely different finding.
   - Compare a **post-ship window against an equal-length pre-ship window**, using the ticket's own ship date (its `completedAt`, or the merge date in a comment/PR link) as the split.
   - Segment the same way the ticket did. If it said Google-organic-only, filter to that — don't silently widen to all traffic.
   - Report the raw numerator and denominator, not just a percentage. `59/884` is auditable; "6.7%" alone is not.

4. **Post one comment per ticket** with `mcp__linear-server__save_comment`. Keep it compact:
   - Days elapsed since ship, and the two windows compared
   - Numerator/denominator and rate for each window
   - **For any event-based metric: the production/preview split, as its own column.** If preview traffic is a meaningful share, say so in the direction line, not in a footnote — "20 clicks, 13 of them Vercel previews" is the finding, "20 clicks" is a wrong one.
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
- 🚨 **The post window must MATCH THE COMPOSITION of the pre window, not just its length.** Equal-length windows are not comparable if they are made of different kinds of days. Before quoting any delta, map both windows to **day-of-week** and compare like against like — weekday vs weekday, weekend vs weekend. State the split and the `n` for each.

  This bites hardest on anything driven by **Kayleigh's own working rhythm** — build counts, deploy-triggered egress, merge volume, admin-dashboard activity, approval-queue depth. It also bites on user-traffic metrics, which have their own weekday/weekend shape.

  Evidence (2026-08-17, NEX-681): a fix merged Friday evening, and the three post-fix days were **Sat, Sun, and a partial Mon**. Measured against an all-days pre-fix average that read as a **−93%** cut in Supabase egress. Split by day-of-week, pre-fix weekends already ran at **~25%** of weekday volume (27.6px vs 110.7px), so the only like-for-like comparison available was **weekend vs weekend: −82%**, with exactly **one** partial weekday post-fix. The change is probably real and large — but −93% was an artifact of window composition, and it was one query away from being caught.

  Practical consequences:
  - A fix that lands Thu/Fri cannot be read before the following week. Say so and name the date that gives a full working week, rather than reporting the weekend as a result.
  - If the post window has `n=1` for the cohort that carries the volume, that is **not enough data** — report it as such, not as a direction.
  - Quote the like-for-like number as the headline. If you also quote the all-days figure, label it as composition-confounded.
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
- **Investigate before escalating.** If a finding has two candidate causes with opposite implications, run the discriminating query and report the answer — don't hand her an open question you could have closed. (2026-08-13: a 7% link-coverage drop looked like silent rot; one query showed 0 stale spans out of 264 and cleared it.) **Bounded to the bright line at the top of this file** — one query that closes the question, not an investigation that opens three more. If closing it needs a design decision or a worktree, `spawn_task` instead.

### Durable formatting note

Prefer tables for anything with more than two dimensions. Bold the number that carries the finding. Lead with bad news when there is bad news.