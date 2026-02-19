# Memory

## Key Findings

- [assistant-ui viewport behavior](assistant-ui-viewport.md) - turnAnchor="top" causes viewport gap during streaming; fix with conditional turnAnchor
- [Debugging library internals](debugging-library-internals.md) - How to investigate @assistant-ui/react source for layout issues (inline styles, ViewportSlack)

## Architecture

- [Citations data flow](citations-data-flow.md) - End-to-end flow from streaming → store → sidebar, auto-scroll logic, extraction timing

## Testing

- [Frontend testing conventions](frontend-testing.md) - vitest + testing-library, commands, store/mock patterns
- [assistant-ui mock patterns](assistant-ui-mocks.md) - Full mock setup for thread.test.tsx, useAssistantState selector gotcha

## Workflow

- [Worktree setup](worktree-setup.md) - Location, env file copy, pnpm, cleanup steps
- **Claude config repo**: `kmigdol/claude-config` at `~/.claude/` — separate git repo for global CLAUDE.md, skills, and project settings. Push changes there (not to NextBest). Note: git tracks the file as `Claude.MD` (not `CLAUDE.md`).

## Patterns

- The `socialgpt-frontend` uses `@assistant-ui/react` for chat UI — library internals can cause unexpected layout issues (inline styles, ViewportSlack min-height)
- Always check library source code in `node_modules/@assistant-ui/react/dist/` when debugging layout issues that don't trace to our own code
- Always use **pnpm** for frontend (never npm), **uv** for backend/dagster

## Agent Lessons

- [Explore agent pitfalls](explore-agent-pitfalls.md) - Explore agents can make wrong claims about framework conventions (e.g. Next.js middleware). Always verify version-specific behavior.
