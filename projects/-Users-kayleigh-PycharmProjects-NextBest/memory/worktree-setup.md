# Git Worktree Setup for This Project

## Location

Worktrees go in: `~/.claude-worktrees/NextBest/<branch-name>/`

## Setup Steps

```bash
# 1. Update main
git fetch origin && git checkout main && git pull origin main

# 2. Create worktree
git worktree add ~/.claude-worktrees/NextBest/<branch-name> -b <branch-name>

# 3. Copy env file (REQUIRED — frontend won't work without it)
cp ~/PycharmProjects/NextBest/socialgpt-frontend/.env.local \
   ~/.claude-worktrees/NextBest/<branch-name>/socialgpt-frontend/.env.local

# 4. Install deps
cd ~/.claude-worktrees/NextBest/<branch-name>/socialgpt-frontend && pnpm install

# 5. Verify baseline
pnpm test -- --run
```

## Important Notes

- **Always use pnpm** for the frontend (never npm — creates conflicting lock file)
- **Always copy .env.local** — it's gitignored and won't be in the worktree
- Backend (`socialgpt/`) uses **uv** (Python)
- Dagster (`socialgpt-dagster/`) uses **uv** (Python)

## Cleanup

```bash
git worktree remove ~/.claude-worktrees/NextBest/<branch-name> --force
```

## Branch Naming

- `feature/nex-<number>-<slug>` — New features
- `fix/nex-<number>-<slug>` — Bug fixes
- `improve/nex-<number>-<slug>` — Improvements
