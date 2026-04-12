def build_response(intent: dict, language: str = "shona") -> dict:
    lang = "en" if language == "en" else "shona"
    answer_steps = intent.get("answer_steps")
    answer_warning = intent.get("answer_warning")
    follow_up_question = intent.get("follow_up_question")

    short = intent.get("answer_short", {}).get(lang, None)
    steps = answer_steps.get(lang, None) if answer_steps is not None else None
    warning = answer_warning.get(lang, None) if answer_warning is not None else None
    follow_up = follow_up_question.get(lang, None) if follow_up_question is not None else None

    return {
        "short": short,
        "steps": steps,
        "warning": warning,
        "follow_up": follow_up,
    }
