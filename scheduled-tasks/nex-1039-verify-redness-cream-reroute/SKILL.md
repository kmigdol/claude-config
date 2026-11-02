---
name: nex-1039-verify-redness-cream-reroute
description: One-time read-only check that the 2026-11-03 daily run drained the NEX-1039 alias merges and re-matched the Physiogel mentions
---

READ-ONLY verification for nextbest Linear ticket NEX-1039. Do NOT write to production: no SQL writes, no pipeline commands with --apply, no proposal-queue apply, no Linear state changes. Only read, then report to Kayleigh, and post one Linear comment (described below).

Context: on 2026-11-02 the following changes were made.
- Product 9863190c-b745-4728-9cb7-038d7cc50370 (slug redness-relief-cream, "Redness Solutions Daily Relief Cream") was moved from brand Physiogel to Clinique (brand_id 2cdfcf45-a241-4e5e-b426-58482cfee63b).
- Its 9 Reddit mentions were really about Physiogel's cream, so a scoped re-match left it with 0 mentions.
- Three merges were then applied, and the 10:00 UTC daily pipeline run on 2026-11-03 should drain their proposal_effects (alias_write and product_ingest):
  - proposal 4800d1bc-0113-4fb7-9368-53b671c1abe6 → aliases "Redness Solutions Cream", "Clinique Redness Solutions Cream", "Redness Solutions Moisturizer" on 9863190c;
  - proposals 7fba68d7-8cb0-4ed1-a786-cbb2bc568df4 ("Redness Relief Cream") and 92f3686f-6459-4a9a-8f92-5fe435dd7683 ("Redness Solutions Daily Relief Cream") → aliases on Physiogel's AI Cream, product 863915ad-cc3e-4e95-9992-8b6bda4e4d53 (slug ai-cream). Before the run, AI Cream had 12 catalog_mentions.

Use the Supabase MCP execute_sql tool for project "nextbest" (project_id rfejgzsgzkfhnaynfjaq; the tool prefix may be mcp__96c2d660-dda4-4822-8b3d-e473824220a1__ or mcp__supabase__). Check:
1. Effects: `select proposal_id, effect_type, status, attempts from proposal_effects where proposal_id in ('4800d1bc-0113-4fb7-9368-53b671c1abe6','7fba68d7-8cb0-4ed1-a786-cbb2bc568df4','92f3686f-6459-4a9a-8f92-5fe435dd7683')`. Expected: all drained (not pending or failed).
2. Aliases: `select product_id, alias from product_aliases where product_id in ('863915ad-cc3e-4e95-9992-8b6bda4e4d53','9863190c-b745-4728-9cb7-038d7cc50370') order by 1,2`.
3. Mentions: catalog_mentions count per product for both ids. Also, for post_ids 1ootkgm, 1reip5y, 1th3htq, 1tz2ff5, 1u98vgl, 1vj5sw8, 1w6136g, 1wb6jde, ay5z6d, the catalog_mentions rows whose product_name_raw ilike '%redness%', with product_id. Expected: they now point at 863915ad (AI Cream).
4. Did the daily run actually run? `select stage_name, last_run_at from pipeline_stage_runs order by last_run_at desc limit 15`.
5. Cards: product_summary_cards rows for both product ids (does each exist, and when was it updated, if that column exists).
6. Live pages: curl -s -o /dev/null -w '%{http_code}' for https://www.nextbest.one/products/ai-cream and https://www.nextbest.one/products/redness-relief-cream. Also check whether the redness-relief-cream page text contains "Clinique" (curl -s … | grep -c Clinique).

Report to Kayleigh in plain language, briefly. Lead with whether the reroute worked: the AI Cream mention count and the 9 threads on AI Cream. Then 9863190c's aliases, mention count and page status. A drop below 3 mentions, and its page going away, is EXPECTED and fine. Flag anything that did not drain or failed, and stop there; suggest no fixes that write. Then post one comment on Linear issue NEX-1039 with the same findings. Find the Linear tools with ToolSearch using the bare verbs "save_comment get_issue"; there are two Linear servers, so use whichever returns tools. Do not change the issue state.