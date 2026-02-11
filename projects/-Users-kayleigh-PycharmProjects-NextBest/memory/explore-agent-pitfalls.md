# Explore Agent Pitfalls

## Problem: Explore agents assume outdated framework conventions

When an Explore agent reads a file and interprets its role, it uses its training knowledge about frameworks — which may be outdated. In NEX-145, the agent saw `proxy.ts` (renamed from `middleware.ts`) and concluded "proxy.ts is NOT integrated as middleware" because it assumed Next.js requires `middleware.ts`. But the project uses **Next.js 16**, which deprecated `middleware.ts` in favor of `proxy.ts`.

## Fix: Tell Explore agents to check versions AND search documentation

When spawning an Explore agent that will analyze framework-specific files, include explicit instructions to:

1. **Check the installed version** of the framework (`package.json` or `node_modules/<pkg>/package.json`)
2. **Search for documentation** when something doesn't match expected conventions — use `WebSearch` to look up the current version's docs rather than relying on training knowledge
3. **Check commit messages** for intentional migrations (e.g. "Migrate middleware.ts to proxy.ts for Next.js 16")
4. **Flag uncertainty** when a file doesn't match expected patterns, rather than asserting it's broken — say "this doesn't match the convention I expect; searching docs to verify" instead of "this is NOT integrated"

## Example prompt addition

> "When analyzing framework-specific files (middleware, config, routing), first check the installed framework version in package.json/node_modules. If anything doesn't match the conventions you expect, use WebSearch to look up the documentation for that specific version before drawing conclusions. Do NOT rely on training knowledge for framework conventions — libraries change between versions. If something looks unusual, check docs and git commit messages for context before concluding it's broken."

## Why documentation search matters

The explore agent has access to `WebSearch` and `WebFetch` but doesn't use them by default for framework questions. Training data has a cutoff, so newer patterns (like Next.js 16's `proxy.ts` replacing `middleware.ts`) will be confidently misidentified as broken code. A 10-second doc search would have caught this.

## General principle

Explore agents are great for finding files and reading content, but their **interpretive claims about framework behavior** should always be verified by searching current documentation. Trust docs + file contents + git history over training knowledge.
