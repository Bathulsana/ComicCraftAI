from pathlib import Path
from uuid import uuid4
import re

from app.config import (
    BASE_DIR,
    GEMINI_API_KEY,
    GEMINI_IMAGE_MODEL,
    HF_API_KEY,
    HF_IMAGE_MODEL,
    HF_IMAGE_PROVIDER,
)


PANELS_DIR = BASE_DIR / "static" / "panels"
PANELS_DIR.mkdir(parents=True, exist_ok=True)


def _safe_filename(text: str) -> str:
    """Create a safe, short filename from prompt text."""
    cleaned = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        text,
    )

    cleaned = cleaned.strip("_")

    if not cleaned:
        cleaned = "panel"

    return cleaned[:50]


def _generate_with_huggingface(
    prompt: str,
    output_path: Path,
) -> None:
    """Generate an image using Hugging Face hosted inference."""

    if not HF_API_KEY:
        raise RuntimeError(
            "HF_API_KEY is missing."
        )

    from huggingface_hub import InferenceClient

    provider = (
        HF_IMAGE_PROVIDER.strip()
        if HF_IMAGE_PROVIDER
        else "auto"
    )

    client = InferenceClient(
        provider=provider,
        api_key=HF_API_KEY,
    )

    image = client.text_to_image(
        prompt=prompt,
        model=HF_IMAGE_MODEL,
        width=768,
        height=768,
        num_inference_steps=25,
        guidance_scale=7.0,
    )

    image.save(output_path)


def _generate_with_gemini(
    prompt: str,
    output_path: Path,
) -> None:
    """Generate an image using Gemini image generation."""

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing."
        )

    from google import genai
    from google.genai import types

    client = genai.Client(
        api_key=GEMINI_API_KEY,
    )

    response = client.models.generate_content(
        model=GEMINI_IMAGE_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            response_format={
                "image": {
                    "aspect_ratio": "1:1",
                    "image_size": "1K",
                }
            },
        ),
    )

    for part in response.parts:
        if part.inline_data:
            image = part.as_image()
            image.save(output_path)
            return

    raise RuntimeError(
        "Gemini did not return an image."
    )


def generate_image(
    image_prompt: str,
    panel_number: int,
) -> str:
    """
    Generate one comic-panel illustration.

    Hugging Face is attempted first.
    Gemini image generation is used as a fallback.
    """

    if not image_prompt or not image_prompt.strip():
        raise ValueError(
            "Image prompt cannot be empty."
        )

    final_prompt = (
        image_prompt.strip()
        + "\n\n"
        "Create a polished comic-style illustration. "
        "Keep the main character visually consistent. "
        "Use clear composition, expressive characters, "
        "good lighting, and strong visual storytelling. "
        "Do not include readable text, captions, speech bubbles, "
        "logos, signatures, or watermarks inside the artwork."
    )

    filename = (
        f"panel_{panel_number}_"
        f"{_safe_filename(image_prompt)}_"
        f"{uuid4().hex[:8]}.png"
    )

    output_path = PANELS_DIR / filename

    errors = []

    # ---------------------------------------------------------
    # 1. Try Hugging Face
    # ---------------------------------------------------------
    if HF_API_KEY:

        try:
            _generate_with_huggingface(
                prompt=final_prompt,
                output_path=output_path,
            )

            if output_path.exists():
                return f"/static/panels/{filename}"

            errors.append(
                "Hugging Face returned no image file."
            )

        except Exception as error:
            errors.append(
                f"Hugging Face image generation failed: {error}"
            )

    else:
        errors.append(
            "HF_API_KEY is not configured."
        )

    # ---------------------------------------------------------
    # 2. Gemini fallback
    # ---------------------------------------------------------
    if GEMINI_API_KEY:

        try:
            _generate_with_gemini(
                prompt=final_prompt,
                output_path=output_path,
            )

            if output_path.exists():
                return f"/static/panels/{filename}"

            errors.append(
                "Gemini returned no image file."
            )

        except Exception as error:
            errors.append(
                f"Gemini image generation failed: {error}"
            )

    else:
        errors.append(
            "GEMINI_API_KEY is not configured."
        )

    # ---------------------------------------------------------
    # 3. If both failed
    # ---------------------------------------------------------
    raise RuntimeError(
        "Could not generate the comic image.\n"
        + "\n".join(
            f"- {message}"
            for message in errors
        )
    )