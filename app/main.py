from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import STATIC_DIR
from app.routes import router


app = FastAPI(
    title="ComicCraftAI",
    version="1.0.0",
    description=(
        "AI-powered five-panel comic story creator "
        "using Gemini and Hugging Face."
    ),
)

# Serve generated images and PDF files.
app.mount(
    "/static",
    StaticFiles(
        directory=str(STATIC_DIR)
    ),
    name="static",
)

# Register application routes.
app.include_router(router)