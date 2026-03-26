# Plan: Commit Linting + Full CI Pipeline

## Context

The project has a basic CI workflow (ruff lint + unit tests + integration tests) but is **missing**:
- Commit message linting (conventional commits)
- MyPy type checking in CI
- Frontend build check in CI
- `ruff format` not in the `check` Makefile target's mypy step

The user wants all quality gates enforced both locally (pre-commit) and in GitHub Actions before code can be merged.

---

## Changes

### 1. Add Conventional Commit Linting (pre-commit hook)

**Modify:** `.pre-commit-config.yaml`
- Add `conventional-pre-commit` hook (Python-based, no Node.js dependency needed in root)
- Enforces types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`
- Runs on `commit-msg` stage

### 2. Update GitHub Actions CI (`.github/workflows/ci.yml`)

Expand from 3 jobs to 6 jobs:

| Job | What it does |
|-----|-------------|
| `commitlint` | Validates PR commit messages follow conventional commits format |
| `lint` | `ruff check .` + `ruff format --check .` (already exists) |
| `typecheck` | `uv run mypy src/` (**new**) |
| `unit-tests` | `uv run pytest tests/unit` (already exists) |
| `integration-tests` | `uv run pytest tests/integration` with PostgreSQL service (already exists) |
| `frontend-build` | `pnpm install && pnpm build` — ensures frontend compiles (**new**) |

- Add Python/uv caching to speed up runs
- Add pnpm caching for frontend job
- Commitlint job uses `wagoid/commitlint-github-action@v6` (standard GitHub Action for this)

### 3. Add Commitlint Config

**New:** `commitlint.config.js`
- Extends `@commitlint/config-conventional`
- Used by the GitHub Action for PR commit validation

**Modify:** `package.json` (new, root-level) — just for commitlint devDependencies
- Or: use the GitHub Action's built-in config support (no root package.json needed)

Actually, `wagoid/commitlint-github-action` can use a config file directly. We'll add a minimal `commitlint.config.js` at root.

### 4. Update Makefile `check` Target

**Modify:** `Makefile`
- Add `$(MYPY) src/` to the `check` target so `make check` runs lint + format + mypy + tests

### 5. Update Pre-commit Hook Versions

**Modify:** `.pre-commit-config.yaml`
- Bump ruff to latest (v0.11.x)
- Bump mypy to latest (v1.15.x)
- Add `conventional-pre-commit` for local commit-msg validation

---

## Files

| File | Action | Purpose |
|------|--------|---------|
| `.pre-commit-config.yaml` | Modify | Add conventional-pre-commit hook, bump versions |
| `.github/workflows/ci.yml` | Modify | Add typecheck, frontend-build, commitlint jobs; add caching |
| `commitlint.config.js` | New | Conventional commit config for GitHub Action |
| `Makefile` | Modify | Add mypy to `check` target |

---

## Verification

1. `make check` — runs lint + format check + mypy + tests locally
2. `pre-commit run --all-files` — ruff + mypy pass
3. `echo "bad message" | pre-commit run conventional-pre-commit --commit-msg-filename /dev/stdin` — rejects
4. `echo "feat: add new feature" | pre-commit run conventional-pre-commit --commit-msg-filename /dev/stdin` — passes
5. Push to branch → GitHub Actions shows all 6 jobs running
