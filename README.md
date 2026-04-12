# Wash Wiki

Wash Wiki is a Bikita-focused sanitation education chatbot knowledge base for rural communities in Bikita District, Zimbabwe. It stores short, practical, culturally relevant guidance about water safety, handwashing, sanitation, and disease prevention in a structured bilingual format that can be consumed by a chatbot, API layer, or future intent-matching service.

The repository is designed around a Shona-first experience. Responses should default to Shona unless a user explicitly asks for English.

## Directory Structure

```text
.
|-- api/
|   `-- README.md
|-- content/
|   |-- disease_prevention.json
|   |-- handwashing.json
|   |-- sanitation.json
|   `-- water_safety.json
|-- logic/
|   `-- contentStore.js
|-- tests/
|   `-- content-store.test.js
|-- Bikita_Sanitation_Bot_Specs-e700e45f-6819-46ba-96b3-de3c7ad71dc8.txt
|-- package.json
`-- README.md
```

## Content Modules

`content/water_safety.json`
Contains the largest intent set covering safe drinking water, river water, home water treatment, boiling, microbial contamination, turbidity, Bikita-specific water quality concerns such as Matezva Dam and mining, and practical decision-based guidance for dirty or limited water access.

`content/handwashing.json`
Contains intents for why handwashing matters, when to wash hands, proper handwashing technique, what to do without soap, and action-oriented fallback guidance using ash.

`content/sanitation.json`
Contains intents for understanding sanitation, why it matters, disease links from poor sanitation, toilet use, open defecation risks, and toilet hygiene practices.

`content/disease_prevention.json`
Contains intents for rainy-season disease risk, cholera outbreak behavior, and broad prevention habits that reinforce water, sanitation, and hygiene actions.

## Intent Data Model

Each intent entry uses a stable schema so downstream intent-recognition and response systems can rely on a consistent contract.

```json
{
  "intent_id": "water_river_safe",
  "topic": "Water Safety",
  "language": "shona/en",
  "canonical_question": {
    "en": "Can I drink river water?",
    "shona": "Ndinganwa mvura yerwizi here?"
  },
  "sample_variations": {
    "en": ["...", "...", "..."],
    "shona": ["...", "...", "..."]
  },
  "answer_short": {
    "en": "...",
    "shona": "..."
  },
  "answer_steps": {
    "en": ["...", "..."],
    "shona": ["...", "..."]
  },
  "answer_warning": {
    "en": "...",
    "shona": "..."
  },
  "follow_up_question": {
    "en": "...",
    "shona": "..."
  },
  "tags": ["keyword1", "keyword2", "keyword3", "keyword4"]
}
```

Field notes:

- `intent_id` is the unique identifier used by retrieval and routing logic.
- `topic` groups the intent into one of the project modules.
- `language` marks the dataset entry as bilingual Shona and English content.
- `canonical_question` stores the normalized user question in both languages.
- `sample_variations` provides alternative phrasings for intent recognition and must include at least 3 English and 3 Shona examples.
- `answer_short` is the primary concise chatbot reply.
- `answer_steps` contains optional step-by-step guidance.
- `answer_warning` contains optional safety or escalation guidance.
- `follow_up_question` contains an optional clarifying or next-step question.
- `tags` provides retrieval keywords for matching and search.

`answer_steps`, `answer_warning`, and `follow_up_question` may be `null` when an intent does not require them.

## Project Purpose

This content store supports later chatbot phases that will:

- recognize user intent from Shona or English input
- retrieve the matching answer payload from the content module files
- keep responses concise and easy to understand in low-bandwidth or mobile-first channels
- preserve a Shona-first user experience for Bikita communities

## Validation

Run the content validation tests with:

```bash
npm test
```
