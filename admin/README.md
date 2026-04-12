# Admin CLI

The admin CLI manages content intents and operational endpoints for the Wash Wiki Python backend.

| Command | Example |
|---|---|
| `list-intents` | `python admin/admin_cli.py list-intents --module water_safety` |
| `add-intent` | `python admin/admin_cli.py add-intent --module water_safety --file new_intent.json` |
| `edit-intent` | `python admin/admin_cli.py edit-intent --module water_safety --intent-id water_river_safe --field answer_short --lang en --value "New answer."` |
| `reload` | `python admin/admin_cli.py reload` |
| `analytics` | `python admin/admin_cli.py analytics` |

## Commands

`list-intents`

Prints each intent ID and English canonical question from `content/<module>.json`.

`add-intent`

Loads a JSON file, validates it against the rules described in [intent_schema.json](/home/tea/Documents/apps/Wash-wiki/admin/intent_schema.json), appends it to the target content module, and writes the updated file back to disk.

`edit-intent`

Updates a localized field on an existing intent. Supported fields are `answer_short`, `answer_warning`, and `follow_up_question`.

`reload`

POSTs to `http://localhost:5000/reload` so the running Flask app reloads content from disk.

`analytics`

GETs `http://localhost:5000/analytics` and prints a formatted usage summary.

## Add-Intent JSON Format

Input files for `add-intent` should follow the structure defined in [intent_schema.json](/home/tea/Documents/apps/Wash-wiki/admin/intent_schema.json).

Required top-level fields:

- `intent_id`
- `topic`
- `language`
- `canonical_question`
- `sample_variations`
- `answer_short`
- `tags`

Expected localized fields:

- `canonical_question.en` and `canonical_question.shona` must be strings.
- `sample_variations.en` and `sample_variations.shona` must be arrays with at least 3 strings each.
- `answer_short.en` and `answer_short.shona` must be strings.
- `tags` must be a non-empty array of strings.
