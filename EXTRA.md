Extra features added
====================

1) Codecov badge placeholder

- A CODECOV_BADGE.md file exists with a placeholder badge and instructions to replace it with the real badge once Codecov receives the coverage upload.

2) Optional LLM-based bullet rewriter

- New endpoint: `POST /api/rewrite-bullets` accepts JSON `{ "role_text": "...", "jd": "..." }`.
- If you set `OPENAI_API_KEY` in the environment (e.g., in `back4app.env`), the server will attempt to call OpenAI to rewrite bullets. If `openai` isn't installed or no key is present, the endpoint falls back to the heuristic bullet generator.
- To enable LLM behavior, add `OPENAI_API_KEY=sk-...` to your `back4app.env` and restart the server.

Security note: Do not commit API keys into the repo. Keep them in `back4app.env` which is ignored by `.gitignore`.
