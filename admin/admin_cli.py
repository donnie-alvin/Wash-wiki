import argparse
import json
import os
import sys
import urllib.error
import urllib.request


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(CURRENT_DIR)
CONTENT_DIR = os.path.join(REPO_ROOT, "content")
SCHEMA_PATH = os.path.join(CURRENT_DIR, "intent_schema.json")


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path, payload):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def module_path(module):
    return os.path.join(CONTENT_DIR, f"{module}.json")


def validate_intent(intent, schema):
    errors = []

    for field in schema.get("required", []):
        if field not in intent:
            errors.append(f"Missing required field: {field}")

    properties = schema.get("properties", {})

    for field in ("canonical_question", "answer_short"):
        field_schema = properties.get(field, {})
        field_value = intent.get(field)
        if not isinstance(field_value, dict):
            errors.append(f"Field '{field}' must be an object.")
            continue

        for required_key in field_schema.get("required", []):
            if required_key not in field_value or not isinstance(field_value.get(required_key), str):
                errors.append(f"Field '{field}.{required_key}' must be a string.")

    sample_schema = properties.get("sample_variations", {})
    sample_variations = intent.get("sample_variations")
    if not isinstance(sample_variations, dict):
        errors.append("Field 'sample_variations' must be an object.")
    else:
        for lang in ("en", "shona"):
            entries = sample_variations.get(lang)
            min_items = sample_schema.get("properties", {}).get(lang, {}).get("minItems", 0)
            if not isinstance(entries, list):
                errors.append(f"Field 'sample_variations.{lang}' must be an array.")
                continue
            if len(entries) < min_items:
                errors.append(f"Field 'sample_variations.{lang}' must have at least {min_items} entries.")
            for index, item in enumerate(entries):
                if not isinstance(item, str):
                    errors.append(f"Field 'sample_variations.{lang}[{index}]' must be a string.")

    tags_schema = properties.get("tags", {})
    tags = intent.get("tags")
    if not isinstance(tags, list):
        errors.append("Field 'tags' must be an array.")
    else:
        if len(tags) < tags_schema.get("minItems", 0):
            errors.append(f"Field 'tags' must have at least {tags_schema.get('minItems', 0)} entries.")
        for index, tag in enumerate(tags):
            if not isinstance(tag, str):
                errors.append(f"Field 'tags[{index}]' must be a string.")

    return errors


def command_list_intents(args):
    intents = load_json(module_path(args.module))
    rows = [(intent["intent_id"], intent["canonical_question"]["en"]) for intent in intents]
    id_width = max([len("Intent ID")] + [len(row[0]) for row in rows])
    question_width = max([len("Canonical Question (EN)")] + [len(row[1]) for row in rows])
    print(f"{'Intent ID':<{id_width}}  {'Canonical Question (EN)':<{question_width}}")
    print(f"{'-' * id_width}  {'-' * question_width}")
    for intent_id, question in rows:
        print(f"{intent_id:<{id_width}}  {question:<{question_width}}")


def command_add_intent(args):
    schema = load_json(SCHEMA_PATH)
    new_intent = load_json(args.file)
    errors = validate_intent(new_intent, schema)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        raise SystemExit(1)

    path = module_path(args.module)
    intents = load_json(path)
    intents.append(new_intent)
    write_json(path, intents)
    print(f"Success: intent '{new_intent['intent_id']}' added to {args.module}.")


def command_edit_intent(args):
    path = module_path(args.module)
    intents = load_json(path)

    for intent in intents:
        if intent.get("intent_id") == args.intent_id:
            if args.field not in ("answer_short", "answer_warning", "follow_up_question"):
                raise SystemExit(f"Unsupported field: {args.field}")
            field_value = intent.setdefault(args.field, {})
            if not isinstance(field_value, dict):
                field_value = {}
                intent[args.field] = field_value
            field_value[args.lang] = args.value
            write_json(path, intents)
            print(f"Updated {args.intent_id}: {args.field}[{args.lang}]")
            return

    raise SystemExit(f"Intent not found: {args.intent_id}")


def _request_json(url, method="GET"):
    request = urllib.request.Request(url, method=method)
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def command_reload(_args):
    try:
        payload = _request_json("http://localhost:5000/reload", method="POST")
    except urllib.error.URLError as exc:
        raise SystemExit(f"Failed to call reload endpoint: {exc}") from exc
    print(json.dumps(payload, indent=2))


def command_analytics(_args):
    try:
        summary = _request_json("http://localhost:5000/analytics")
    except urllib.error.URLError as exc:
        raise SystemExit(f"Failed to call analytics endpoint: {exc}") from exc

    print("=== Analytics Summary ===")
    print(f"Total sessions:      {summary.get('total_sessions', 0)}")
    print(f"Total messages:      {summary.get('total_messages', 0)}")
    print(f"Intent match rate:   {summary.get('intent_match_rate', 0.0) * 100:.0f}%")
    print(f"Fallback rate:       {summary.get('fallback_rate', 0.0) * 100:.0f}%")
    print(f"Escalations:         {summary.get('escalations', 0)}")
    print()
    print("Top Intents:")
    top_intents = summary.get("top_intents", [])
    if top_intents:
        for index, item in enumerate(top_intents, start=1):
            print(f"  {index}. {item['intent_id']}  ({item['count']})")
    else:
        print("  None")
    print()
    print("Language Breakdown:")
    language_breakdown = summary.get("language_breakdown", {})
    if language_breakdown:
        for language, count in language_breakdown.items():
            print(f"  {language}:    {count}")
    else:
        print("  None")


def build_parser():
    parser = argparse.ArgumentParser(description="Wash Wiki admin CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list-intents")
    list_parser.add_argument("--module", required=True)
    list_parser.set_defaults(func=command_list_intents)

    add_parser = subparsers.add_parser("add-intent")
    add_parser.add_argument("--module", required=True)
    add_parser.add_argument("--file", required=True)
    add_parser.set_defaults(func=command_add_intent)

    edit_parser = subparsers.add_parser("edit-intent")
    edit_parser.add_argument("--module", required=True)
    edit_parser.add_argument("--intent-id", required=True)
    edit_parser.add_argument("--field", required=True)
    edit_parser.add_argument("--lang", choices=("en", "shona"), required=True)
    edit_parser.add_argument("--value", required=True)
    edit_parser.set_defaults(func=command_edit_intent)

    reload_parser = subparsers.add_parser("reload")
    reload_parser.set_defaults(func=command_reload)

    analytics_parser = subparsers.add_parser("analytics")
    analytics_parser.set_defaults(func=command_analytics)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
