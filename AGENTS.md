# AGENTS.md — CaciqueAnalytics

## Model Switching Protocol

Model switching is **manual** — the user runs `/model <name>` in the terminal.
The agent only reminds when it's time to switch.

1. **Thinking/Planning phase** — Use **DeepSeek V4 Pro** for:
   - Brainstorming and requirements exploration
   - Design discussions and architecture decisions
   - Researching libraries (LanusStats, alternatives)
   - Writing implementation plans (use `writing-plans` skill)

2. **Implementation phase** — Switch to **Kimi v2.6** for:
   - Writing production code
   - Running tests and debugging
   - Executing implementation plans

When analysis is complete, the agent must remind the user:
> "Planning done. Switch to Kimi v2.6: `/model kimi-v2.6`"

## Windows Environment

- All shell commands must be **PowerShell 7+ compatible**
- Use full cmdlet names: `Get-ChildItem` (not `ls`), `Set-Location` (not `cd`), `Remove-Item` (not `rm`)
- Use `;` for sequential commands, `&&` for conditional chaining
- Quote paths containing spaces with double quotes
- No `sudo`, no `brew`, no Unix-only tools
- Python: use `python` not `python3`. Node: use `npm`/`npx` directly.
- File paths: Use Windows-style backslashes or forward slashes (both work in pwsh)

## No Emojis

Do not use emojis in any output, commit messages, code comments, or documentation. Zero exceptions.

## Project Context

**CaciqueAnalytics** is a data pipeline for Chilean football analytics:

- **Data source**: LanusStats library (SofaScore wrapper) + direct API calls
- **Scope**: Primera Division Chile, Copa de la Liga, Copa Libertadores, Copa Sudamericana (2025-2026)
- **Pipeline**: Extract (SofaScore) -> Transform/Clean -> Load to PostgreSQL -> Generate data layers -> Export JSON -> User designs infographics in Canvas
- **Cadence**: Automated updates after each gameday (Phase 4 in progress)
- **Current state**: Data layers complete (player, comparison, leaderboard), HTML renderer built, 21 tests passing
- **Output**: Structured JSON files in `Infographics/data/` for manual infographic creation

## Essential Rules

### Code
- No unnecessary comments. Code should be self-documenting.
- Follow existing code conventions when modifying files.
- Never assume a library is available — verify it's in the project first.
- Never commit secrets, API keys, or `.env` files. Use `.env.example` for templates.

### Testing
- Always write tests for new features or bugfixes.
- Run the full test suite before claiming work is complete.
- Use `verification-before-completion` skill before declaring anything done.

### Git

After every meaningful advance (feature complete, bug fixed, test passing):

1. Ask the user for permission before committing or pushing. Never do either
   automatically.
2. Run tests first — only proceed if they pass.
3. Stage changes and commit with conventional format: `type(scope): description`
   - Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`
4. Push to remote after commit (with user permission).

- Never force push to main/master.
- Never skip hooks (`--no-verify`, `--no-gpg-sign`) unless user explicitly requests it.

### Autoskills (Tech-Stack Skills)

Before starting any implementation work, run `npx autoskills` to auto-detect the
tech stack and install curated skills from the autoskills registry
(https://www.autoskills.sh). This ensures the agent has domain-specific
knowledge for the libraries in use.

- Run `npx autoskills --dry-run` first to preview what would be installed.
- Run `npx autoskills -y` to install all detected skills.
- Expected skills for this project (depending on final stack): Python patterns,
  pandas, pytest, data analysis, scikit-learn, SQLAlchemy, or similar.
- Re-run after adding new dependencies to pick up new skills.

### Skills

**Superpowers (auto-loaded):**
- Use `brainstorming` before any creative work or design decisions.
- Use `writing-plans` for multi-step implementation tasks.
- Use `systematic-debugging` when encountering bugs — before proposing fixes.
- Use `test-driven-development` when implementing features or fixes.
- Use `verification-before-completion` before claiming work is complete.

**Matt Pocock Skills (installed via `npx skills`):**
- `diagnose` — Disciplined debugging loop
- `grill-me` / `grill-with-docs` — Interview-style requirements grind
- `tdd` — Test-driven development with red-green-refactor
- `zoom-out` — High-level system perspective on unfamiliar code
- `to-prd` — Synthesize discussion into a PRD
- `to-issues` — Break plans into grabbable issues
- `triage` — Triage issues through state machine
- `caveman` — Ultra-compressed communication (save tokens)
- `improve-codebase-architecture` — Find deepening opportunities
- `prototype` — Throwaway prototype for design questions
- `write-a-skill` — Create new skills
- `setup-matt-pocock-skills` — Scaffold per-repo config

### Handover Protocol (for /compact)

Before using `/compact` (or when context is about to be lost), the agent must
write a handover summary to `CONTEXT.md` with these sections:

```
# Current Task
- What we're building right now (1 sentence)
- Which phase/section of PLAN.md we're executing
- Which files are in progress

# Last Actions
- What was just done (last 3-5 actions with results)
- What was verified/tested

# Next Actions
- Exact next step (with file paths)
- Any blockers or decisions pending

# Critical State
- DB connection info (no passwords)
- Environment details
- Model currently in use
- Open branches / uncommitted changes
```

After `/compact`, the agent reads `CONTEXT.md` first to recover state.

### Security

- Never store passwords in any file. Use `$env:PGPASSWORD` in session only.
- Database credentials live in `.env` (not committed). Template in `.env.example`.
- All installed skills (autoskills, mattpocock/skills) are audited for safety.
- Review `security_audit_report.md` when adding new dependencies or skills.
- X/Twitter API keys: never commit, never log, never echo.

## Data Pipeline Conventions

- All ETL scripts must be idempotent (safe to re-run).
- Database migrations must be versioned and reversible.
- X (Twitter) API interactions must handle rate limits gracefully.
- Data processing must be fast enough to post pre-match and post-match within the engagement window.
- Validate incoming data against expected schemas — Chilean league data can be inconsistent.
