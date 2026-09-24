---
name: catalog-review
description: Weekday research of pending alias_flag, new_product, duplicate_product, new_tag and new_brand taxonomy proposals with parallel web agents, plus INCI agents for new products and the INCI gap queue (NEX-840); writes verdicts and INCI lists into each proposal's dossier, loads spot-checked gap lists, and replies with a digest (no Linear comment). Never changes a proposal's status unattended; when Kayleigh is present it walks her through the decision classes and applies only what she approves.
---

Daily catalog audit for the nextbest taxonomy proposal queue. It researches pending proposals with parallel web-research agents, writes the verdicts into each proposal's own dossier fields, and reports a digest. **Report only — you must never change a proposal's status.**

Follow `.claude/skills/catalog-audit/SKILL.md` in the repo at `/Users/kayleigh/dev/nextbest` —
the **MAIN checkout**, not a worktree. That file is the authority on the helper's flags, the
research prompts, the dossier fields `write-research` writes, and the digest format; this file
says what a scheduled run does with them. Read it first, every run.

Repo: `/Users/kayleigh/dev/nextbest`. **The digest is the reply only — post NO Linear comment.**
NEX-798 left Monitoring (2026-09-15) and Kayleigh said to stop commenting on it; do not look for
another ticket to post to. SKILL.md's "post it as a Linear comment" steps do not apply to this
routine — this line overrides them.

## 🚨 Unattended means report-only

**Never run `apply`. Never change any proposal's status. Never approve, reject, merge, delete,
promote or reassign anything.** `apply` is the only command that resolves a proposal, and it runs
only in the walkthrough, only on Kayleigh's explicit "approve `<class>`" for a class she named.

`counts`, `list`, `inci-input` and `write-research` are the whole unattended surface of the helper.
`write-research` writes research into `dossier_json` on rows that stay `pending` — that is the
deliverable, and it is not a status change. The pipeline side (NEX-840) is `nextbest inci-gap`
(read-only), `nextbest inci-spot-check` (no database) and **`nextbest load-inci`, the one
production write this routine makes unattended** (Kayleigh, 2026-09-23) — only on the checked gap
files, only through step 5b's gates.

## 🚨 Finish the digest before acting on anything

Research every lane you pulled, write the research back, and reply with the digest **before**
starting work on any individual finding. The digest is a single deliverable; a half-finished digest
plus an hour on one interesting card leaves the rest of the run with no record. This holds when
Kayleigh redirects mid-run: say you are finishing the digest first (it takes a minute), then pick up
her request.

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
5. `grep` is aliased to ugrep on this machine — use `/usr/bin/grep -a` or `rg`. Never wrap a helper
   command in `timeout` (macOS has none) and never pipe one through `tail` without capturing its
   exit code first (redirect to a file, then `echo "EXIT=$?"`); a masked exit code has produced a
   false "it worked" before.

## The five lanes

`alias_flag`, `new_product`, `duplicate_product`, `new_tag`, `new_brand`. **SKILL.md's lane-coverage
table under "Score before trust" is the authority on which the routine may pull** — as of
2026-09-18 every lane says yes, both new_tag and new_brand having been scored against Kayleigh's own
resolutions that day. If a row there ever says otherwise, honour it and say so in the digest.

Pull order and caps, oldest first:

| order | lane | cap | note |
|---|---|---|---|
| 1 | `alias_flag` | 100 | |
| 2 | `new_product` | 100 | raised from 40 on 2026-09-24 (Kayleigh) — the lane with the backlog |
| 3 | `duplicate_product` | 100 | usually empty; a pair is two products we already carry |
| 4 | `new_tag` | 100 | small lane |
| 5 | `new_brand` | **40** | SECOND WAVE — see below; brand cards are the heaviest (raised from 20 on 2026-09-24) |

**`new_brand` is pulled only AFTER `new_product`'s `write-research` has run.** A pending product
joins a brand's bundle only once its own dossier says `approve` with `researched_at`, so today's
product research is what makes a brand approvable. Pull it as a second wave, after step 5 for the
other lanes, then research and write it the same way.

## Steps

1. **Before-snapshot.**

   ```
   cd /Users/kayleigh/dev/nextbest/frontend && npx -y tsx scripts/proposal-queue.ts counts --env .env.prod
   ```

   Keep the JSON line. It goes in the digest and is the baseline for any after-snapshot.

2. **Pull the first four lanes**, capped as above. Write the queue files into
   `/private/tmp/catalog-audit-<YYYY-MM-DD>/` (create it) and **state the paths you used** in the
   digest so a later walkthrough can find them. `--out` is REQUIRED on every `list`.

   ```
   cd /Users/kayleigh/dev/nextbest/frontend && npx -y tsx scripts/proposal-queue.ts list --lane <lane> --status pending --limit <cap> --out /private/tmp/catalog-audit-<date>/queue-<lane>.json --env .env.prod
   ```

   Record what each `list` prints — the precheck line, the SKU blocker breakdown, the category
   vocabulary line, and (default pulls only) `re-researchable (brand-struck no_attach)`. `list`
   excludes rows this skill already stamped, so each run walks forward through the backlog.
   **If every lane comes back with `count: 0`, post a one-line digest and stop.**

3. **Batch and dispatch.** Split each lane's `cards` into batches of ~20, each its own JSON file
   (a `new_tag` batch keeps the file's `categories_by_vertical`). Then one `Agent` call per batch,
   **all in a single message** so they run concurrently: `subagent_type: "general-purpose"`,
   `model: "opus"` (fall back to `"sonnet"` if an Opus rate limit is reported),
   `run_in_background: true`. Give each agent its batch file path, a distinct output path, and the
   matching lane prompt from SKILL.md **verbatim**. Wait for every agent to finish.

   `new_brand` agents also need a brands file — write it first with a read-only query against
   production and put the path in the prompt (the SKILL.md step names the query).

   Tell each agent to write its findings file after every 3–4 cards and to use a helper-script
   filename containing its batch number (on 2026-09-16 two agents stalled with nothing saved, and
   two shared one script name and overwrote each other's output).

   **INCI agents, in the same message (NEX-840).** A product with no INCI list shows no ingredient
   chips. Follow SKILL.md Step 1's INCI section exactly:

   ```
   cd /Users/kayleigh/dev/nextbest/frontend && npx -y tsx scripts/proposal-queue.ts inci-input --queue /private/tmp/catalog-audit-<date>/queue-new_product.json --out /private/tmp/catalog-audit-<date>/inci --batch-size 10
   cd /Users/kayleigh/dev/nextbest && railway run --service nextbest -- pipeline/.venv/bin/python -m nextbest inci-gap --write-batches /private/tmp/catalog-audit-<date>/inci-gap --batch-size 10
   ```

   The second command is read-only against production; record the coverage and `overdue` lines it
   prints. Then one agent per `inci_input_NN.json` and per `inci_gap_*_input.json`, each with
   SKILL.md's **INCI agent prompt** verbatim, 10 products per agent — the batch size the blind
   accuracy runs measured. Each writes beside its input, `_input` → `_output`
   (`inci/inci_output_01.json`, `inci-gap/inci_gap_<stamp>_batch_01_output.json`). Do not fold INCI
   work into the verdict agents.

4. **Consolidate, validate, and run the within-lane duplicate pass.** Merge each lane's batch
   outputs into one `findings-<lane>.json`. Check exactly one finding per `card_id`, no extras or
   duplicates. **Every finding whose `recommendation` is not `undecided` must carry at least one
   citation URL** — downgrade any that does not to `undecided` with `undecided_reason: "no citable
   source"`, because `write-research` aborts the entire run on the first uncited one. Then run the
   within-lane duplicate pass exactly as SKILL.md Step 2 describes, and report its count in the form
   that section requires — a single-batch lane says so rather than reporting a bare 0.

5. **Write the research back**, per lane. Record the `written N / skipped M (not pending) /
   needs_enrichment K` line from each — all three numbers go in the digest.

   For `new_product`, add `--inci` with the queue's INCI agent outputs, comma-separated
   (`--inci /private/tmp/catalog-audit-<date>/inci/inci_output_01.json,…`). Record its
   `inci: attached N` line. The lists ride on the proposals and are written when Kayleigh approves.

5b. **Load the gap-queue lists (NEX-840)**, following SKILL.md Step 1's three gates exactly and
   stopping on the first non-zero exit:

   ```
   cd /Users/kayleigh/dev/nextbest && pipeline/.venv/bin/python -m nextbest inci-spot-check /private/tmp/catalog-audit-<date>/inci-gap/*_output.json --out /private/tmp/catalog-audit-<date>/inci-gap/checked
   cd /Users/kayleigh/dev/nextbest && railway run --service nextbest -- pipeline/.venv/bin/python -m nextbest load-inci /private/tmp/catalog-audit-<date>/inci-gap/checked/*_checked.json
   cd /Users/kayleigh/dev/nextbest && railway run --service nextbest -- pipeline/.venv/bin/python -m nextbest load-inci /private/tmp/catalog-audit-<date>/inci-gap/checked/*_checked.json --apply --coverage
   ```

   - Run the dry run and read its plan BEFORE the apply. **If the chip-row `delete` count is not 0,
     do not apply** — report the plan in the digest. (`protected (other source)` above 0 is normal.)
   - Load only files `inci-spot-check` wrote (`*_checked.json`) — never an agent's raw output.
   - If the spot check keeps no rows, there is nothing to load; say so.
   - Record the spot check's summary line and the apply's `--coverage` output.

6. **Second wave: `new_brand`.** Now pull it (cap 40), research it, validate it and write it back,
   exactly as steps 2–5 (5b is not repeated: the gap queue is loaded once per run).

7. **Read back what is now decidable**, per lane, with `--researched-only`, and group by
   `agent.decision_class` for the digest's class counts. This includes rows earlier runs researched
   and nobody has actioned yet — that backlog is exactly what the digest is for.

8. **Reply with the digest.** No Linear comment.

## What the digest must carry, beyond the class counts

SKILL.md Step 3 has the template. The parts that are easy to get wrong:

- **`new_brand`: say what an approve would CREATE** — per approvable brand, its aliases, then each
  sendable SKU as `name · category · attach N · aliases` with struck spellings marked. A bare count
  is unreadable as a result.
- **Never report a single `blocked N` for SKUs.** `attach_zero` (nobody mentions the product) and
  `no_attach` (our own research struck every alias — self-inflicted, and re-researchable once) are
  opposite failures; report them separately, and the two `undecided:no_approvable_sku` lines keyed
  on them.
- **`new_tag`: show the name that would be created** when house casing moves it
  (`precheck.created_name`), with the proposed spelling beside it.
- **`undecided` is a finding, not a failure**, and `needs_enrichment` is not an error.
- **No single accuracy number, ever.** Counts per decision class; the classes speak for themselves.
- **Report raw numerator and denominator**, never a bare rate.
- **INCI (NEX-840):** `inci: attached N` on the new_product write-back; how many INCI rows came back
  null, with the agents' reasons; `inci-gap`'s coverage and `overdue` lines before the load; the
  spot check's `pass / fail / unreachable / unresolved` line with every dropped row and why; the
  load's written counts and the `--coverage` output after it. Overdue > 0 after the load is the
  headline, not a footnote.
- **`precheck-blocked` is a queue-health signal** — break it down by failing gate, since which gate
  dominates says what would unblock the most rows.

## When Kayleigh is present

Only if she replies in this session. Then run SKILL.md's **Present mode** walkthrough: one lane per
walkthrough, several decision classes per message, each headed by its three plain-language sentences
from SKILL.md's tables, each closed by its own yes/no line, with one combined "N decisions" prompt at
the bottom. Then wait.

Before building any `decisions.json`, **run the read-back duplicate pass over
`researched-<lane>.json`** that SKILL.md Step 4 requires — the whole stamped backlog, not just
today's findings. Two approvals of the same thing from different days is exactly what it catches.

On her explicit approval of a **named** class: build `decisions.json` for that class from the cards'
`agent` blocks, run `apply --dry-run` and show the printed request list, then `apply --group <class>`
with `--base-url https://www.nextbest.one --env .env.prod`, then report the ledger summary
(`ok / noop / skipped / failed`, every skipped and failed row with its reason, and the caveat "a
failed row may still have been consumed — check the row before retrying"). Then the next class.

- **A `delete` class goes through the APPROVE route** (`delete_product_alias`), so approving it is an
  approve, not a reject. If auto mode blocks that production call, ask Kayleigh to allow it or print
  the command — never work around it.
- **An `ORPHAN BRAND` line is reported to her verbatim and never auto-fixed.**
- **A `duplicate_product` merge sends no request** — print the `merge-products` dry-run and apply
  commands and record the row as `manual`.
- A class she did not name is untouched: not held, not rejected, still pending for `/admin/taxonomy`.
- At the end, take a `counts` after-snapshot and report it beside the before, with the promote
  narration (a `promote` creates a NEW pending `new_product` row, so that count *rises*).
- **INCI gap lists are loaded by the unattended run itself** (step 5b). If it stopped at a gate,
  show her the plan it stopped on and ask before re-running.

## Failure handling

- **Any helper command exiting non-zero: stop.** Do not run the next command, do not apply anything.
  Put the command and its error in the digest and reply — a run that stopped early with a stated
  reason is a finding; a silent partial run is not.
- **An agent batch that fails or returns unusable JSON:** consolidate the batches that succeeded, run
  `write-research` on those, and list the failed batch's `card_id`s in the digest under
  `unresearched` with the reason. Never invent findings for them.
- **A `write-research` abort on validation:** fix the findings file (downgrade the uncited findings
  to `undecided`) and re-run it. Do not pass a hand-edited recommendation.
- **Do not spin up investigations.** If a finding turns into work — a detector looks wrong, a brand
  is mis-modelled, the queue has a structural problem — say so in one line and, if it matters,
  `spawn_task` it. This routine researches rows; it never fixes the code emitting them.