import json
import re

from google import genai
from google.genai import types

from app.config import (
    GEMINI_API_KEY,
    GEMINI_TEXT_MODEL,
    GEMINI_TEXT_FALLBACK_MODEL,
)


def _get_client():
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add your Gemini API key to the .env file."
        )

    return genai.Client(api_key=GEMINI_API_KEY)


def _parse_json_response(text: str):
    cleaned = (text or "").strip()

    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned,
    )

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:

        object_match = re.search(
            r"\{.*\}",
            cleaned,
            flags=re.DOTALL,
        )

        array_match = re.search(
            r"\[.*\]",
            cleaned,
            flags=re.DOTALL,
        )

        candidate = None

        if object_match:
            candidate = object_match.group(0)
        elif array_match:
            candidate = array_match.group(0)

        if candidate is None:
            raise ValueError(
                "Gemini returned a response that could not be converted to JSON."
            )

        try:
            return json.loads(candidate)
        except json.JSONDecodeError as error:
            raise ValueError(
                "Gemini returned invalid JSON."
            ) from error


def generate_story(outline: list[dict]) -> list[dict]:
    outline_text = json.dumps(
        outline,
        ensure_ascii=False,
        indent=2,
    )

    prompt = f"""
Turn this five-panel comic outline into polished comic writing.

COMIC OUTLINE:
{outline_text}

Return JSON only using exactly this structure:

{{
  "panels": [
    {{
      "panel_number": 1,
      "caption": "Short caption.",
      "narration": "Short narration.",
      "dialogue": [
        {{
          "speaker": "Character name",
          "line": "Short dialogue."
        }}
      ]
    }}
  ]
}}

Rules:

1. Return exactly five panels.
2. Keep the same panel numbers.
3. Keep the story consistent with the supplied outline.
4. Make captions short.
5. Make narration clear and engaging.
6. Keep dialogue natural and short enough for a comic panel.
7. Dialogue may be an empty list when a panel does not need dialogue.
8. Do not use Markdown.
9. Do not add extra JSON fields.
""".strip()

    client = _get_client()

    models_to_try = [
        GEMINI_TEXT_MODEL,
    ]

    if (
        GEMINI_TEXT_FALLBACK_MODEL
        and GEMINI_TEXT_FALLBACK_MODEL != GEMINI_TEXT_MODEL
    ):
        models_to_try.append(
            GEMINI_TEXT_FALLBACK_MODEL
        )

    response = None
    last_error = None

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.8,
                    max_output_tokens=3500,
                    response_mime_type="application/json",
                ),
            )
            break

        except Exception as error:
            error_code = getattr(
                error,
                "code",
                None,
            )

            if error_code not in (
                500,
                503,
                504,
            ):
                raise

            last_error = error

    if response is None:
        raise RuntimeError(
            "Gemini story generation failed with both "
            "the primary and fallback models."
        ) from last_error

    data = _parse_json_response(response.text)

    panels = data.get("panels") if isinstance(data, dict) else data

    if not isinstance(panels, list):
        raise ValueError("Gemini did not return story panels.")

    if len(panels) != 5:
        raise ValueError(
            f"Expected story content for 5 panels, but received {len(panels)}."
        )

    normalized_panels = []

    for index, panel in enumerate(panels, start=1):

        if not isinstance(panel, dict):
            raise ValueError(
                f"Story panel {index} is invalid."
            )

        dialogue = panel.get("dialogue", [])

        if not isinstance(dialogue, list):
            dialogue = []

        cleaned_dialogue = []

        for line in dialogue:
            if isinstance(line, dict):
                cleaned_dialogue.append(
                    {
                        "speaker": str(
                            line.get(
                                "speaker",
                                "Character",
                            )
                        ).strip(),
                        "line": str(
                            line.get(
                                "line",
                                "",
                            )
                        ).strip(),
                    }
                )

        normalized_panels.append(
            {
                "panel_number": index,
                "caption": str(
                    panel.get(
                        "caption",
                        "",
                    )
                ).strip(),
                "narration": str(
                    panel.get(
                        "narration",
                        "",
                    )
                ).strip(),
                "dialogue": cleaned_dialogue,
            }
        )

    return normalized_panels