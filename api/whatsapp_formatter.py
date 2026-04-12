def format_whatsapp_reply(fm_response: dict) -> str:
    parts = []

    base_text = fm_response.get("response_text") or fm_response.get("short")
    if base_text:
        parts.append(base_text)

    steps = fm_response.get("steps")
    if isinstance(steps, list) and steps:
        parts.append("")
        parts.extend(f"{index}. {step}" for index, step in enumerate(steps, start=1))

    warning = fm_response.get("warning")
    if isinstance(warning, str) and warning.strip():
        parts.append("")
        parts.append(f"\u26a0\ufe0f {warning.strip()}")

    follow_up = fm_response.get("follow_up")
    if isinstance(follow_up, str) and follow_up.strip():
        parts.append("")
        parts.append(follow_up.strip())

    if fm_response.get("is_fallback") is True:
        topic_menu = fm_response.get("topic_menu")
        if isinstance(topic_menu, list) and topic_menu:
            parts.append("")
            parts.append("You can ask about:")
            parts.extend(
                f"{index}. {topic}" for index, topic in enumerate(topic_menu, start=1)
            )

    return "\n".join(parts).rstrip()[:4096]
