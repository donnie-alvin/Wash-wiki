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
        f"You are a rural health and sanitation assistant for Bikita District. "
        f"Answer using only the provided knowledge base. Do not add facts, advice, or recommendations that are not in the knowledge base. "
        f"Do not diagnose illness or provide treatment advice. If the user describes severe illness or an emergency, tell them to go to the nearest clinic or contact a health worker. "
        f"If the question is outside sanitation, hygiene, water safety, or disease prevention topics covered by the knowledge base, say that you can only help with those topics and ask the user to rephrase or ask about one of them. "
        f"Keep the response to 1 to 3 short sentences. Respond in {language_label} language."
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
