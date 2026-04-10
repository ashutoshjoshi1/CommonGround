# Schema Reference

Primary tables:

- `users`
- `workspaces`
- `workspace_members`
- `sources`
- `source_versions`
- `source_chunks`
- `embedding_metadata`
- `prompts`
- `prompt_versions`
- `runs`
- `run_steps`
- `retrieved_chunks`
- `evaluations`
- `evaluation_items`
- `feedback`
- `audit_events`
- `findings`
- `tags`
- `tag_links`
- `jobs`
- `workspace_settings`

Migration strategy:

- Alembic configured under `apps/api/alembic`
- initial migration `20260410_0001_initial.py`
