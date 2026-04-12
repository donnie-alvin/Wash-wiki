import logging
import os

import openai


def get_ai_response(user_input: str, language: str, all_intents: list[dict]) -> str | None:
    if os.environ.get("AI_ENABLED", "true").lower() != "true":
        return None
    if not os.environ.get("OPENAI_API_KEY"):
        return None

    model = os.environ.get("AI_MODEL", "gpt-4o-mini")
    timeout_seconds = int(os.environ.get("AI_TIMEOUT_SECONDS", "8"))
    language_label = "Shona" if language == "shona" else "English"
    system_prompt = (
        "You are a sanitation and water safety assistant for rural communities in "
        "Bikita District, Zimbabwe. You help people understand safe water practices, "
        "handwashing, sanitation, and disease prevention. Answer only from the "
        "knowledge base provided. Keep answers to 1 to 3 short sentences. Use simple "
        "words. Do not diagnose illness. Do not replace a health worker. If someone "
        "describes a severe emergency, tell them to go to the nearest clinic. If the "
        "question is outside the knowledge base, say you cannot help with that and "
        "suggest they ask about water safety, handwashing, sanitation, or disease "
        f"prevention. Respond in {language_label} language."
    )
    kb_text = "\n".join(
        f"[{intent['intent_id']}] Q: {intent['canonical_question']['en']} | A: {intent['answer_short']['en']}"
        for intent in all_intents
    )
    user_prompt = f"Knowledge base:\n{kb_text}\n\nUser question: {user_input}"

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=200,
            temperature=0.2,
            timeout=timeout_seconds,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        logging.getLogger(__name__).warning("AI response failed: %s", exc)
        return None
