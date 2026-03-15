# Copilot Instructions - CaciqueAnalytics

## Language and style

- Code, variables and function names in English.
- Comments and documentation in Spanish.
- Keep answers concise and technically precise.

## Security

- Never hardcode secrets.
- Use .env for credentials.
- Prefer least privilege for database users.

## Model routing policy (manual selection)

Use cheap models for low-risk work and Codex models for critical engineering tasks.

- Quick questions and docs: Claude Haiku 4.5.
- Simple rewrites/refactors: Claude Sonnet 4/4.5 or GPT-5 mini.
- ETL design, data quality, idempotency, architecture decisions: GPT-5.3-Codex.
- Complex debugging and deep code review: GPT-5.3-Codex or Claude Sonnet 4.6.

Note: model switching cannot be forced automatically by repository files in current Copilot behavior.
Note: in this workspace flow, switching to Anthropic models requires opening a new chat.
