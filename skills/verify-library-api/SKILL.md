---
name: verify-library-api
description: Use when using any framework or library API, especially fast-moving libraries like Dagster, LangGraph, assistant-ui, or Next.js — prevents assuming outdated API patterns
---

# Verify Library API Before Using

## Overview

Libraries change between versions. API patterns from training data may be outdated.

**Core principle:** Check the installed version and verify the API matches BEFORE writing code that uses it.

## When to Use

**Use when:**
- Calling any framework/library API you haven't verified this session
- A library API doesn't behave as expected
- Spawning an agent to work with framework-specific code
- Upgrading or installing a new package version

**Especially for:** Dagster, LangGraph, assistant-ui, Next.js, and any rapidly-evolving library.

## Steps

### 1. Check Installed Version

```bash
# Python
pip show <package> | grep Version
uv pip show <package> | grep Version

# Node.js
pnpm list <package>
cat node_modules/<package>/package.json | grep version
```

### 2. Verify API Matches That Version

**In order of reliability:**
1. Read actual source in `node_modules/` or `site-packages/` (most reliable)
2. Check changelog for breaking changes between your known version and installed version
3. Search docs for the installed version: `WebSearch("<library> <version> <api-name> documentation")`

### 3. When Spawning Agents

When dispatching explore or implementation agents for framework-specific code, include:

```markdown
IMPORTANT: Check the installed version of <framework> before making claims
about conventions or expected patterns. If anything doesn't match what you
expect, use WebSearch to look up documentation for that specific version.
Do NOT rely on training knowledge for framework conventions — flag
uncertainty rather than asserting code is broken.
```

## Common Mistakes

**Trusting training knowledge over installed version**
- Training data has a cutoff. Newer patterns (e.g., Next.js 16 `proxy.ts` replacing `middleware.ts`) will be confidently misidentified as broken code.

**Checking docs but not the version**
- Docs for v3 don't apply to your v2 install. Always check version first.

**Skipping verification for "well-known" APIs**
- Even stable libraries make breaking changes. 30 seconds to verify saves hours debugging.

## Red Flags

- "I know this API" — verify anyway, it may have changed
- "The docs say..." — which version's docs?
- "This file is wrong / not integrated" — did you check the framework version first?
- An explore agent claims code "doesn't follow convention" — verify the convention for the installed version
