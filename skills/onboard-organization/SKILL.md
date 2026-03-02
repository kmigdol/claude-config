---
name: onboard-organization
description: Use when onboarding a new organization — adding creators, ingesting content, running taxonomy gap analysis, and verifying dashboard visibility
---

# Onboard Organization

## Overview

Brand intelligence onboarding workflow for beauty industry organizations. Takes a spreadsheet of creators through to a fully functional dashboard with content, catalog matching, and taxonomy coverage.

**Announce at start:** "I'm using the onboard-organization skill to set up this organization."

## When to Use

- New organization needs to be set up in the system
- Adding a batch of creators for an existing org
- Re-onboarding after significant catalog changes

## Prerequisites

- Creator spreadsheet (name, handles, type, categories, notes)
- Supabase MCP access
- Prefect server access (for content ingestion)
- `socialgpt-prefect` repo (for taxonomy gap analysis script)

## Steps

### Step 1: Parse Spreadsheet

- Extract creator name, handles (TikTok/Instagram), type, categories, notes
- Normalize handles: strip `@`, lowercase
- Validate: no duplicate handles, platform specified

### Step 2: Create/Verify Organization

Check if org exists:

```sql
SELECT * FROM organizations WHERE slug = '<org-slug>';
```

If new, create:

```sql
INSERT INTO organizations (name, slug) VALUES ('<Org Name>', '<org-slug>');
```

### Step 3: Add Creators

Insert creators, tracked_handles, organization_creators (with categories), creator_annotations.

**Key:** Categories go in `organization_creators.categories` (`text[]` array, per-org), NOT `creator_annotations.category`.

Use batch inserts where possible.

```sql
-- Insert creator
INSERT INTO creators (name, type) VALUES ('Creator Name', 'individual');

-- Insert tracked handle
INSERT INTO tracked_handles (creator_id, platform, handle)
VALUES ('<creator_id>', 'tiktok', 'handlename');

-- Link to org with categories
INSERT INTO organization_creators (org_id, creator_id, categories)
VALUES ('<org_id>', '<creator_id>', ARRAY['skincare', 'makeup']);

-- Optional annotations
INSERT INTO creator_annotations (creator_id, notes)
VALUES ('<creator_id>', 'Focus: clean beauty');
```

### Step 4: Trigger Content Ingestion

- Run Prefect content ingestion pipeline (full or targeted by creator handles)
- Monitor pipeline progress in Prefect UI
- Wait for completion before proceeding

### Step 5: Link Platform Author IDs

Critical for connecting tracked_handles to actual content:

```sql
UPDATE tracked_handles th
SET platform_author_id = ca.id
FROM content_authors ca
WHERE lower(ca.handle) = lower(th.handle)
  AND ca.platform = th.platform
  AND th.platform_author_id IS NULL;
```

**Key gotcha:** Must use `lower()` on BOTH sides for case-insensitive matching.

Verify linkage:

```sql
SELECT count(*) FROM tracked_handles
WHERE platform_author_id IS NULL
  AND creator_id IN (
    SELECT creator_id FROM organization_creators WHERE org_id = '<org_id>'
  );
```

### Step 6: Taxonomy Gap Analysis

Run the standalone script:

```bash
cd socialgpt-prefect
uv run python scripts/taxonomy_gap_analysis.py --org-slug <org-slug>
```

Review output with user -- shows unmatched brands/topics with frequency and suggested actions (`add_new` vs `add_alias`).

**Deduplication -- prefer aliases over new entries:**
- Before adding a new brand/topic, search the existing catalog for near-matches (the script's fuzzy matching helps, but also check manually for synonyms, abbreviations, and variant spellings)
- If an unmatched entity is a variant of an existing entry, add it as an **alias** rather than a new entity -- this prevents catalog bloat and keeps matching accurate
- Example: "The Ordinary" and "TO" should be aliases of the same brand, not two separate brands
- When in doubt, add an alias -- it's easier to promote an alias to a new entity later than to merge duplicates

Add approved entities to catalog:
- `brands` requires `normalized_name` column
- `brand_aliases` requires `normalized_alias` column
- Same pattern for topics/topic_aliases and products/product_aliases

### Step 7: Re-run Catalog Matching

After taxonomy additions, re-match content against updated catalog.

- Use Prefect catalog matching pipeline with `clear_existing=True` to rebuild all matches
- This populates `content_catalog_mentions`

### Step 8: Verify Roster Visibility

Two filters must be satisfied for dashboard visibility:

1. Creator is member of the organization (`organization_creators`)
2. Creator has recent videos (content linked via `tracked_handles.platform_author_id`)

- Check frontend dashboard shows creators with content
- Verify coverage metrics look reasonable

## Quick Reference

| Step | Action | Key Table(s) |
|------|--------|---------------|
| 1 | Parse spreadsheet | -- |
| 2 | Create org | `organizations` |
| 3 | Add creators | `creators`, `tracked_handles`, `organization_creators`, `creator_annotations` |
| 4 | Ingest content | `content_metadata`, `content_raw_extraction` |
| 5 | Link authors | `tracked_handles`, `content_authors` |
| 6 | Taxonomy gaps | `brands`, `topics`, aliases tables |
| 7 | Re-match catalog | `content_catalog_mentions` |
| 8 | Verify dashboard | -- |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Categories in `creator_annotations.category` | Use `organization_creators.categories` (per-org, `text[]` array) |
| Adding new entities without checking for duplicates | Always search existing catalog first; prefer adding aliases over new entries |
| Case-sensitive handle matching | Always use `lower()` on both sides |
| Missing `normalized_name` on brands | Required field -- set to `lower(name)` or similar |
| Missing `normalized_alias` on aliases | Required field -- set to `normalize_text(alias)` |
| Skipping author ID linking | Content won't appear on dashboard without this step |
| Running taxonomy analysis before content ingestion | Need `content_raw_extraction` data first |

## Red Flags

- **Dashboard shows 0 creators** -- Check `organization_creators` join
- **Creators show but no content** -- Check `tracked_handles.platform_author_id` linkage
- **Low coverage after taxonomy additions** -- Re-run catalog matching with `clear_existing=True`
- **Unlinked handles after Step 5** -- Handle case mismatch or content not yet ingested for that creator

## Related Skills

- `starting-linear-ticket` -- for creating the onboarding ticket and PR workflow
- `using-git-worktrees` -- for isolated workspace during taxonomy additions
