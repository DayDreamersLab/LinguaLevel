from collections import OrderedDict
import json
import os
import re

from openai import OpenAI


FALLBACK_MAP = {
    "analyze": "study",
    "approximately": "about",
    "assistance": "help",
    "commence": "start",
    "comprehend": "understand",
    "consequence": "result",
    "demonstrate": "show",
    "distribute": "share",
    "eliminate": "remove",
    "encounter": "meet",
    "facilitate": "help",
    "fundamental": "basic",
    "implement": "do",
    "individuals": "people",
    "maintain": "keep",
    "methodology": "method",
    "numerous": "many",
    "objective": "goal",
    "obtain": "get",
    "participate": "join",
    "possess": "have",
    "prioritize": "focus on first",
    "requirement": "need",
    "sufficient": "enough",
    "utilize": "use",
}

LEVEL_NOTES = {
    "A1": "Use very basic vocabulary and short sentences.",
    "A2": "Use simple everyday vocabulary and mostly short sentences.",
    "B1": "Use clear, common words and straightforward sentence structure.",
    "B2": "Keep language clear and practical, with moderate sentence complexity.",
    "C1": "Use advanced but still learner-friendly academic language.",
    "C2": "Keep the meaning accurate and polished with near-native fluency.",
}


def simplify_text(text: str, level: str) -> tuple[str, list[dict[str, str]]]:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if api_key:
        return simplify_with_openai(text, level, api_key)
    return simplify_with_fallback(text)


def simplify_with_openai(text: str, level: str, api_key: str) -> tuple[str, list[dict[str, str]]]:
    client = OpenAI(api_key=api_key)
    prompt = f"""
You are helping non-native English students.
Rewrite the material so its vocabulary and sentence complexity match CEFR level {level}.
{LEVEL_NOTES[level]}

Return strict JSON with this schema:
{{
  "simplified_text": "...",
  "removed_vocab": [
    {{"original": "...", "replacement": "...", "meaning": "..."}}
  ]
}}

Rules:
- Keep core meaning and key facts.
- Replace difficult words with easier alternatives for the target level.
- removed_vocab must include only words/phrases that were actually simplified.
- meaning should be a short learner-friendly definition in English.
""".strip()

    response = client.responses.create(
        model="gpt-5-mini",
        input=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ],
        text={"format": {"type": "json_object"}},
    )

    payload = json.loads(response.output_text)
    simplified = payload.get("simplified_text", text)
    removed_vocab = payload.get("removed_vocab", [])
    cleaned_vocab = []
    for item in removed_vocab:
        original = str(item.get("original", "")).strip()
        replacement = str(item.get("replacement", "")).strip()
        meaning = str(item.get("meaning", "")).strip()
        if original and replacement and meaning:
            cleaned_vocab.append(
                {
                    "original": original,
                    "replacement": replacement,
                    "meaning": meaning,
                }
            )
    return simplified, cleaned_vocab


def simplify_with_fallback(text: str) -> tuple[str, list[dict[str, str]]]:
    replacements = OrderedDict()

    def repl(match: re.Match) -> str:
        token = match.group(0)
        key = token.lower()
        if key in FALLBACK_MAP:
            new_word = FALLBACK_MAP[key]
            if token[0].isupper():
                new_word = new_word.capitalize()
            replacements[key] = new_word
            return new_word
        return token

    simplified = re.sub(r"\b[A-Za-z][A-Za-z'-]*\b", repl, text)
    vocab_list = [
        {
            "original": original,
            "replacement": replacement,
            "meaning": f"{replacement} is a simpler way to say {original}.",
        }
        for original, replacement in replacements.items()
    ]
    return simplified, vocab_list
