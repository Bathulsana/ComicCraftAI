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

    # Remove optional Markdown code fences.
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

        # Try to recover a JSON object or array if extra text was returned.
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


def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> list[dict]:
    prompt = f"""
Create a polished five-panel comic outline.

USER STORY IDEA:
{story_prompt}

MAIN CHARACTER:
{character_name}

SETTING:
{setting}

STORY TONE:
{tone}

ART STYLE:
{art_style}

Return JSON only using exactly this structure:

{{
  "panels": [
    {{
      "panel_number": 1,
      "title": "Panel title",
      "scene_description": "What visually happens in the scene.",
      "image_prompt": "Detailed prompt for generating the illustration."
    }}
  ]
}}

Rules:

1. Return exactly five panels.
2. Panel numbers must be 1, 2, 3, 4, and 5.
3. Maintain the same main character throughout the story.
4. Give the story a clear beginning, development, turning point, and ending.
5. Make every panel visually different enough to be interesting.
6. Keep the requested setting, tone, and art style consistent.
7. Make image prompts detailed and useful for image generation.
8. Do not ask the image model to draw captions, speech bubbles, written dialogue,
   logos, watermarks, or other text inside the image.
9. Use only the requested JSON structure.
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
                    temperature=0.75,
                    max_output_tokens=3000,
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
            "Gemini text generation failed with both "
            "the primary and fallback models."
        ) from last_error

    data = _parse_json_response(response.text)

    panels = data.get("panels") if isinstance(data, dict) else data

    if not isinstance(panels, list):
        raise ValueError("Gemini did not return a panel list.")

    if len(panels) != 5:
        raise ValueError(
            f"Expected exactly 5 panels, but Gemini returned {len(panels)}."
        )

    normalized_panels = []

    for index, panel in enumerate(panels, start=1):

        if not isinstance(panel, dict):
            raise ValueError(
                f"Panel {index} was not returned as a valid object."
            )

        normalized_panels.append(
            {
                "panel_number": index,
                "title": str(
                    panel.get(
                        "title",
                        f"Panel {index}",
                    )
                ).strip(),
                "scene_description": str(
                    panel.get(
                        "scene_description",
                        "",
                    )
                ).strip(),
                "image_prompt": str(
                    panel.get(
                        "image_prompt",
                        "",
                    )
                ).strip(),
            }
        )

    return normalized_panels