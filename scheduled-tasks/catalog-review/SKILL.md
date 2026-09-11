---
name: catalog-review
description: Daily research of pending alias_flag and new_product taxonomy proposals with parallel web agents; writes verdicts into each proposal's dossier and posts a digest on NEX-798. Report-only unattended — applies nothing; when Kayleigh is present it walks her through the decision classes and applies only what she approves.
---

Daily catalog audit for the nextbest taxonomy proposal queue. It researches pending
`alias_flag` and `new_product` proposals with parallel web-research agents, writes the verdicts
into each proposal's own dossier fields, and reports a digest. **Report only — you must never
change a proposal's status.**

Follow `.claude/skills/catalog-audit/SKILL.md` in the repo at `/Users/kayleigh/dev/nextbest` —
the **MAIN checkout**, not a worktree. That file is the authority on the helper's flags, the
research prompts, the dossier fields `write-research` writes, and the digest format; this file
says what a scheduled run does with them. Read it first, every run.

Repo: `/Users/kayleigh/dev/nextbest`. Linear team: `Nextbest` (key NEX). Post the digest as a
comment on **NEX-798** while that ticket is open; if it is Done or Canceled, post no comment and
just reply with the digest.

## 🚨 Unattended means report-only

**Never run `apply`. Never change any proposal's status. Never approve, reject, merge, delete,
promote or reassign anything.** `apply` is the only command that resolves a proposal, and it runs
only in the walkthrough, only on Kayleigh's explicit "approve `<class>`" for a class she named.

`counts`, `list` and `write-research` are the whole unattended surface. `write-research` writes
research into `dossier_json` on rows that stay `pending` — that is the deliverable, and it is not
a status change.

## 🚨 Finish the digest before acting on anything

Research both lanes, write the research back, and post the digest **before** starting work on any
individual finding. The digest is a single deliverable; a half-posted digest plus an hour on one
interesting card leaves the rest of the run with no record. This holds when Kayleigh redirects
mid-run: say you are finishing the digest first (it takes a minute), then pick up her request.

## 🚨 There are TWO Linear MCP servers

`linear-server` is the one that keeps failing auth. The other is UUID-named —
`mcp__5afa51ff-6015-498e-9e18-a1d1d62866c2__*` — exposes the same tools against the same
workspace, and has been live on every occasion `linear-server` was not. **The string "linear"
appears NOWHERE in its tool names**, so searching for "linear" returns nothing and it looks like
Linear is simply unavailable.

Before writing any sentence saying Linear is unavailable, search by the **bare tool verb**:

```
ToolSearch → select:mcp__5afa51ff-6015-498e-9e18-a1d1d62866c2__get_issue,mcp__5afa51ff-6015-498e-9e18-a1d1d62866c2__save_comment
```

The startup reminder that `linear-server` needs authentication is a statement about that one
server instance, not about Linear. Only after a bare-verb search returns nothing may you say
Linear is unreachable — and then still reply with the digest, saying the comment could not be
posted.

## Preconditions

1. **`frontend/.env.prod` must exist.** It holds the production Supabase URL and service key.
   Every helper command in this routine passes `--env .env.prod` explicitly.
2. **If `frontend/.env.prod` is missing, STOP.** Reply saying the routine could not run and that
   the file needs copying from wherever the prod credentials live. **Never fall back to
   `.env.local`** — that is the local Supabase mirror, and researching it would burn agent time
   writing findings into the wrong database, invisible to production.
3. `--base-url https://www.nextbest.one` belongs to `apply` only, which this routine never runs
   unattended. No `--base-url` appears in any unattended command.
4. All commands run from `frontend/` of the main checkout (`cd /Users/kayleigh/dev/nextbest/frontend`).

## Steps

1. **Before-snapshot.**

   ```
   cd /Users/kayleigh/dev/nextbest/frontend && npx -y tsx scripts/proposal-queue.ts counts --env .env.prod
   ```

   Keep the JSON line. It goes in the digest and is the baseline for any after-snapshot.

2. **Pull both lanes**, capped at 40 cards each, oldest first. Write the queue files into
   `/private/tmp/catalog-audit-<YYYY-MM-DD>/` (create it) and **state the paths you used** in the
   digest so a later walkthrough can find them.

   ```
   cd /Users/kayleigh/dev/nextbest/frontend && npx -y tsx scripts/proposal-queue.ts list --lane alias_flag --status pending --limit 40 --out /private/tmp/catalog-audit-<date>/queue-alias_flag.json --env .env.prod
   cd /Users/kayleigh/dev/nextbest/frontend && npx -y tsx scripts/proposal-queue.ts list --lane new_product --status pending --limit 40 --out /private/tmp/catalog-audit-<date>/queue-new_product.json --env .env.prod
   ```

   `list` excludes rows this skill already stamped, so each run walks forward through the backlog.
   **If both files come back with `count: 0`, post a one-line digest ("nothing unresearched in
   either lane") and stop.**

3. **Batch and dispatch.** Split each lane's `cards` into batches of ~20, each its own JSON file
   (`batch-alias_flag-01.json` …) with the same shape as the queue file. Then one `Agent` call per
   batch, **all in a single message** so they run concurrently: `subagent_type:
   "general-purpose"`, `model: "opus"` (fall back to `"sonnet"` if an Opus rate limit is
   reported), `run_in_background: true`. Give each agent its batch file path, a distinct output
   path (`findings-alias_flag-01.json` …), and the matching lane prompt from SKILL.md
   **verbatim**. Wait for every agent to finish before continuing.

4. **Consolidate and validate.** Merge each lane's batch outputs into one
   `findings-<lane>.json`: `{ "lane": "<lane>", "findings": [ … ] }`. Check exactly one finding
   per `card_id`, no extras or duplicates. **Every finding whose `recommendation` is not
   `undecided` must carry at least one citation URL** — downgrade any that does not to
   `undecided` with `undecided_reason: "no citable source"` rather than shipping it, because
   `write-research` aborts the entire run on the first uncited non-undecided finding. Confirm
   `reassign`/`merge` findings carry `target_product_id` and `promote` findings carry
   `new_product_name`.

5. **Write the research back**, per lane:

   ```
   cd /Users/kayleigh/dev/nextbest/frontend && npx -y tsx scripts/proposal-queue.ts write-research --queue /private/tmp/catalog-audit-<date>/queue-<lane>.json --file /private/tmp/catalog-audit-<date>/findings-<lane>.json --env .env.prod
   ```

   Record the `written N / skipped M (not pending) / needs_enrichment K` line from each run — all
   three numbers go in the digest.

6. **Read back what is now decidable**, per lane, for the digest's class counts:

   ```
   cd /Users/kayleigh/dev/nextbest/frontend && npx -y tsx scripts/proposal-queue.ts list --lane <lane> --researched-only --out /private/tmp/catalog-audit-<date>/researched-<lane>.json --env .env.prod
   ```

   Group those cards by `agent.decision_class`. This includes rows earlier runs researched and
   nobody has actioned yet — that backlog is exactly what the digest is for.

7. **Post the digest** as a Linear comment on NEX-798 (while open), then reply with it.

## When Kayleigh is present

Only if she replies in this session. Then run SKILL.md's **Present mode** walkthrough:

- **One lane per walkthrough**, `alias_flag` first while `new_product` is still being proven.
- Work through the `decision_class` groups from `researched-<lane>.json`, **several classes per
  message** (all of them at once is fine while each holds ~10 rows or fewer; a class with more than
  ~10 gets its own message), each headed by its three plain-language sentences from SKILL.md's
  tables and closed by its own yes/no line, with one combined "N decisions" prompt at the bottom.
  Then wait for her answer.
- On her explicit approval of a **named** class, build `decisions.json` for that class from the
  cards' `agent` blocks, run `apply --dry-run` and show the printed request list, then run
  `apply --group <class>` (with `--base-url https://www.nextbest.one --env .env.prod`), then
  report the ledger summary (`ok / noop / skipped / failed`, every skipped/failed row with its
  reason, and the caveat "a failed row may still have been consumed — check the row before
  retrying"). Then the next approved class.
- **A `delete` class goes through the approve route** (`delete_product_alias`), so approving it is
  an approve, not a reject. If Claude Code's auto mode blocks that production delete call, **ask
  Kayleigh to allow it or print the command for her to run** — never work around it.
- **`new_product` rows show the image, the Amazon link and the Stylevana link** (or its
  `stylevana_suppressed_reason` and score), and say which rows would launch with no buy link. If
  Kayleigh supplies an ASIN, follow SKILL.md's three-step procedure — verify the listing title
  first, then the `status = 'pending'`-guarded dossier update, then `apply --dry-run`.
- A class she did not name is untouched: not held, not rejected, still pending for
  `/admin/taxonomy`.
- At the end, take a `counts` after-snapshot and post it as a comment alongside the before, with
  the promote narration (a `promote` creates a NEW pending `new_product` row, so `new_product`
  pending *rises* — say the number or the delta reads as a regression).

## Failure handling

- **Any helper command exiting non-zero: stop.** Do not run the next command, do not apply
  anything. Put the command and its error in the digest and post it — a run that stopped early
  with a stated reason is a finding; a silent partial run is not.
- **An agent batch that fails or returns unusable JSON:** consolidate the batches that succeeded,
  run `write-research` on those, and list the failed batch's `card_id`s in the digest under
  `unresearched` with the reason. Never invent findings for them.
- **A `write-research` abort on validation:** fix the findings file (downgrade the uncited
  findings to `undecided`) and re-run it. Do not pass a hand-edited recommendation.
- **Linear unreachable after the two-server check:** still reply with the digest, and say the
  comment could not be posted.

## Judgement rules

- **Lead with what needs a decision.** The digest's job is to say which classes are ready for a
  human, not to narrate the run.
- **No single accuracy number, ever.** Never summarise the agents' work as a percentage. Report
  counts per decision class and let the classes speak.
- **`undecided` is a finding, not a failure.** It routes a row to a human with a reason. A run
  with many undecideds and citations everywhere beats one with confident uncited answers.
- **Never describe a class as "clean" if any of its rows lacks a citation.** Say how many rows in
  the class carry a citation URL, out of how many.
- **`needs_enrichment` is not an error.** It means the pipeline has not finished its mechanical
  work on that row, so we deliberately left it alone. Report the count; do not chase it.
- **`precheck-blocked` is a queue-health signal.** Break it down by failing gate (brand /
  category / image / attach) — which gate dominates says what would unblock the most rows.
- **Report the raw numerator and denominator**, never a bare rate — "12 of 40 alias_flag cards".
- **Do not spin up investigations.** If a finding turns into work — a detector looks wrong, a
  brand is mis-modelled, the queue has a structural problem — say so in one line and, if it
  matters, `spawn_task` it. This routine researches rows; it never fixes the code emitting them.

## Output

### Step 1 — the digest (always)

Post as a Linear comment on NEX-798 (while open) and reply with the same text:

```
**catalog-audit — <date>** · run <duration> · pending before: alias_flag <N>, new_product <N>

**alias_flag** — <N> researched (<N> left unresearched) · these are PRODUCT aliases, not tags
| what the research recommends | n | class |
|---|---|---|
| Keep the alias — it is the product's former name | 12 | `keep:rename` |
| Remove the alias — it names more than one product | 4 | `delete:ambiguous_shorthand` |
undecided 6 · needs_enrichment 0 · precheck-blocked 0

**new_product** — <N> researched (<N> left unresearched)
| Do not add it — the same product we already carry | 9 | `merge:same_sku` |
undecided 11 · needs_enrichment 6 · precheck-blocked 8 (brand 3 / category 1 / image 2 / attach 2)

Queue files: /private/tmp/catalog-audit-<date>/
Nothing was applied. Say `walk alias_flag` to go through them.
```

**Never head a class with its code label.** The first cell is that class's **Recommended** sentence
from SKILL.md's plain-language tables, shortened to a line; the code label rides in the last column.
`alias_flag` rows are PRODUCT aliases — Reddit spellings attached to a product — not tag aliases;
say so. Then the `undecided`, `needs_enrichment` and `precheck-blocked` tallies (the last by failing
gate), the run duration and the `counts` before-snapshot. **The digest is the whole deliverable for
an unattended run. Stop there.**

### Step 2 — the walkthrough (only when Kayleigh is present)

Several classes per message, each in this shape, one combined prompt at the bottom:

> ## <lane> — <K> classes, <N> decisions
>
> ### <plain-language heading> (`<decision_class>`) — <count> rows
> **Proposed:** <sentence>   **Recommended:** <sentence>   **Approving:** <sentence>
> - *<alias or product name>* → <what the agent found> · <citation URL>
> - … `show <decision_class>` for every row. → **<its own yes/no question>**
>
> ### <next class, same shape> …
>
> **<N> decisions above. Reply `yes to all`, or name the classes you want.**

Rules: the three sentences come **verbatim from SKILL.md's plain-language tables** — a code label is
never a heading, only a parenthetical. Split a class into its own message only when it has more than
~10 rows. **Give a recommendation, not a menu**; say plainly when the call is genuinely hers, and
order classes by how much they unblock, not alphabetically. Present the `undecided` classes too, so
she can see what the agents could not settle — they generate no request and take no approval.