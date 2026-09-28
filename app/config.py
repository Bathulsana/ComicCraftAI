import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

# Load variables from the project's .env file.
load_dotenv(BASE_DIR / ".env")


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
HF_API_KEY = os.getenv("HF_API_KEY", "").strip()

# Current Gemini text model.
GEMINI_TEXT_MODEL = os.getenv(
    "GEMINI_TEXT_MODEL",
    "gemini-3.8-flash",
).strip()

GEMINI_TEXT_FALLBACK_MODEL = os.getenv(
    "GEMINI_TEXT_FALLBACK_MODEL",
    "gemini-3.5-flash-lite",
).strip()

# Current Gemini native image-generation model.
GEMINI_IMAGE_MODEL = os.getenv(
    "GEMINI_IMAGE_MODEL",
    "gemini-3.1-flash-image",
).strip()

# Hugging Face image model.
HF_IMAGE_MODEL = os.getenv(
    "HF_IMAGE_MODEL",
    "stabilityai/stable-diffusion-3-medium-diffusers",
).strip()

HF_IMAGE_PROVIDER = os.getenv(
    "HF_IMAGE_PROVIDER",
    "hf-inference",
).strip()

# Create required directories automatically.
STATIC_DIR = BASE_DIR / "static"
PANELS_DIR = STATIC_DIR / "panels"
EXPORTS_DIR = STATIC_DIR / "exports"

PANELS_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)