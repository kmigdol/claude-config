---
name: Vercel stale build cache
description: Vercel preview builds can use stale .next cache causing missing data — may need clean rebuild
type: feedback
---

Vercel preview deployments can cache stale SSG data from previous builds, causing missing tag IDs or other data issues that look like code bugs but aren't.

**Why:** Discovered during NEX-31 when product sorting appeared broken on preview but worked locally — the preview had a cached `.next` directory missing 7 of 13 concern tag IDs.

**How to apply:** If a preview deployment shows unexpected data issues (missing fields, wrong values), suspect stale Vercel cache before debugging code. A fresh build (or pushing a new commit) should fix it. For SSG apps, data changes in Supabase also require a rebuild to show up.
