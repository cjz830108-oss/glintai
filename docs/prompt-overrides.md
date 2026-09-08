# Prompt Runtime Overrides — prompt_templates / prompt_versions

The fiction engine's agent prompts live in `api/_lib/prompts.js` (server-side only).
Any agent's **SYSTEM prompt** can be overridden at runtime **without redeploying**, via two
Supabase tables. The engine checks overrides every 5 minutes per instance and fails open
to built-in prompts if the DB is unreachable or the tables are empty.

## Agent keys

| key | role |
|---|---|
| `story_architect` | blueprint design |
| `character_director` | cast building |
| `plot_planner` | chapter outline (chunked) |
| `novel_writer` | chapter prose |
| `continuity_editor` | contradiction check |
| `literary_editor` | prose polish |
| `quality_scorer` | 9-axis scoring |
| `memory_updater` | memory extraction |
| `reviser` | quality-gate rewrite |
| `reader_simulator` | 3-persona reader simulation |
| `action` | targeted chapter actions |

## How to override (Supabase Dashboard → SQL Editor or Table Editor)

```sql
-- 1) register the template
insert into public.prompt_templates (key, name, current_version)
values ('novel_writer', 'Novel Writer (tuned)', 1)
on conflict (key) do update set current_version = excluded.current_version;

-- 2) add the replacement SYSTEM prompt as a version
insert into public.prompt_versions (template_id, version, body)
select id, 1, 'You are the Novel Writer ... your new system prompt here ...'
from public.prompt_templates where key = 'novel_writer';
```

- `body` = the **replacement SYSTEM prompt**. The user prompt (with its parameter
  placeholders like `${ctx}`) stays as coded — it carries the data plumbing.
- To change again: bump `current_version` and insert a new `prompt_versions` row with
  that version number. Old versions are kept (audit trail).
- To roll back: set `current_version` back to a lower version that exists.
- To remove an override entirely: `delete from prompt_templates where key = '...'`.

## Behavior notes

- Cached 5 min per serverless instance → changes take effect within ~5 minutes.
- If `prompt_templates` has no row for a key, the built-in prompt is used.
- If the current_version row is missing in `prompt_versions`, built-in is used.
- Never paste secrets into prompts; they are sent to model providers verbatim.
