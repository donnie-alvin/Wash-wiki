"""Decision tree follow-up prompts and branch routing."""

from __future__ import annotations


DECISION_TREES = {
    "dirty_water_action": {
        "follow_up_question": (
            "Is it very cloudy or just slightly dirty? / "
            "Mvura yakasviba zvikuru here kana zvishoma?"
        ),
        "branches": {
            "very_cloudy": {
                "short": "Very cloudy water needs extra cleaning first.",
                "steps": [
                    "Filter the water first using a clean cloth or sand filter.",
                    "Boil it after filtering before drinking.",
                ],
                "warning": "Do not drink very cloudy water before filtering and boiling.",
            },
            "slightly_dirty": {
                "short": "Slightly dirty water still needs treatment.",
                "steps": [
                    "Boil the water before drinking.",
                    "Keep it in a clean, covered container.",
                ],
                "warning": "Do not drink slightly dirty water without boiling it.",
            },
        },
    },
    "water_cloudy_clean": {
        "follow_up_question": (
            "Is it very cloudy or just slightly dirty? / "
            "Mvura yakasviba zvikuru here kana zvishoma?"
        ),
        "branches": {
            "very_cloudy": {
                "short": "Very cloudy water needs extra cleaning first.",
                "steps": [
                    "Filter the water first using a clean cloth or sand filter.",
                    "Boil it after filtering before drinking.",
                ],
                "warning": "Do not drink very cloudy water before filtering and boiling.",
            },
            "slightly_dirty": {
                "short": "Slightly dirty water still needs treatment.",
                "steps": [
                    "Boil the water before drinking.",
                    "Keep it in a clean, covered container.",
                ],
                "warning": "Do not drink slightly dirty water without boiling it.",
            },
        },
    },
    "handwash_no_soap": {
        "follow_up_question": "Do you have ash available? / Une madota here?",
        "branches": {
            "yes_ash": {
                "short": "You can use ash to clean your hands if soap is not available.",
                "steps": [
                    "Rub ash on wet hands well, including between fingers.",
                    "Rinse your hands with clean water.",
                ],
                "warning": "Use only clean ash and clean water if possible.",
            },
            "no_ash": {
                "short": "Use the cleanest option you have and get soap when you can.",
                "steps": [
                    "Rinse hands with clean running water as well as possible.",
                    "Wash with soap as soon as you can get some.",
                ],
                "warning": "Hand cleaning without soap or ash is less effective.",
            },
        },
    },
    "no_soap_action": {
        "follow_up_question": "Do you have ash available? / Une madota here?",
        "branches": {
            "yes_ash": {
                "short": "You can use ash to clean your hands if soap is not available.",
                "steps": [
                    "Rub ash on wet hands well, including between fingers.",
                    "Rinse your hands with clean water.",
                ],
                "warning": "Use only clean ash and clean water if possible.",
            },
            "no_ash": {
                "short": "Use the cleanest option you have and get soap when you can.",
                "steps": [
                    "Rinse hands with clean running water as well as possible.",
                    "Wash with soap as soon as you can get some.",
                ],
                "warning": "Hand cleaning without soap or ash is less effective.",
            },
        },
    },
    "water_river_safe": {
        "follow_up_question": (
            "Is the water clear or dirty? / "
            "Mvura yakachena here kana yakasviba?"
        ),
        "branches": {
            "clear": {
                "short": "Clear water can still contain invisible germs.",
                "steps": [
                    "Boil the water before drinking.",
                    "Store it in a clean, covered container.",
                ],
                "warning": "Clear river water is not automatically safe to drink.",
            },
            "dirty": {
                "short": "Dirty river water needs extra treatment before drinking.",
                "steps": [
                    "Filter the water first with a clean cloth or sand filter.",
                    "Boil the water after filtering.",
                ],
                "warning": "Do not drink dirty river water without filtering and boiling.",
            },
        },
    },
    "river_water_action": {
        "follow_up_question": (
            "Is the water clear or dirty? / "
            "Mvura yakachena here kana yakasviba?"
        ),
        "branches": {
            "clear": {
                "short": "Clear water can still contain invisible germs.",
                "steps": [
                    "Boil the water before drinking.",
                    "Store it in a clean, covered container.",
                ],
                "warning": "Clear river water is not automatically safe to drink.",
            },
            "dirty": {
                "short": "Dirty river water needs extra treatment before drinking.",
                "steps": [
                    "Filter the water first with a clean cloth or sand filter.",
                    "Boil the water after filtering.",
                ],
                "warning": "Do not drink dirty river water without filtering and boiling.",
            },
        },
    },
}

BRANCH_KEYWORDS = {
    "very_cloudy": {"very", "cloudy", "zvikuru", "chaizvo"},
    "slightly_dirty": {"slightly", "dirty", "zvishoma", "shoma"},
    "yes_ash": {"yes", "ash", "hongu", "madota"},
    "no_ash": {"no", "ash", "kwete", "hapana", "madota"},
    "clear": {"clear", "clean", "yakachena", "chena"},
    "dirty": {"dirty", "murky", "yakasviba", "sviba"},
}


def resolve_branch(intent_id: str, user_input: str) -> dict | None:
    tree = DECISION_TREES.get(intent_id)
    if tree is None:
        return None

    lowered_input = user_input.lower()
    words = set(lowered_input.split())

    for branch_key, response in tree["branches"].items():
        keywords = BRANCH_KEYWORDS.get(branch_key, set())
        if any(keyword in lowered_input or keyword in words for keyword in keywords):
            return response
    return None


def get_follow_up_question(intent_id: str) -> str | None:
    tree = DECISION_TREES.get(intent_id)
    if tree is None:
        return None
    return tree["follow_up_question"]
