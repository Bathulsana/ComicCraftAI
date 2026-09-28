from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request,
)
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR
from app.schemas import PromptRequest
from app.services.comic_service import generate_comic
from app.services.image_generator import generate_image


templates = Jinja2Templates(
    directory=str(
        BASE_DIR / "templates"
    )
)

router = APIRouter()


def _friendly_error(
    error: Exception,
) -> str:

    message = str(error).strip()

    if message:
        return message

    return (
        "An unexpected error occurred "
        "while generating the comic."
    )


@router.get("/")
def home(
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@router.post("/generate")
def generate(
    request: Request,
    story_prompt: str = Form(
        ...,
        min_length=3,
        max_length=2000,
    ),
    character_name: str = Form(
        "Alex",
        min_length=1,
        max_length=100,
    ),
    setting: str = Form(
        "A modern city",
        min_length=1,
        max_length=200,
    ),
    tone: str = Form(
        "adventurous",
        min_length=1,
        max_length=100,
    ),
    art_style: str = Form(
        "comic book",
        min_length=1,
        max_length=100,
    ),
):

    try:

        result = generate_comic(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context=result,
        )

    except Exception as error:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": _friendly_error(error),
                "story_prompt": story_prompt,
                "character_name": character_name,
                "setting": setting,
            },
            status_code=500,
        )


@router.post("/generate-comic/json")
def generate_comic_json(
    payload: PromptRequest,
):

    try:

        result = generate_comic(
            story_prompt=payload.story_prompt,
            character_name=payload.character_name,
            setting=payload.setting,
            tone=payload.tone,
            art_style=payload.art_style,
        )

        return JSONResponse(
            content=result
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=_friendly_error(error),
        ) from error


@router.get("/export-success")
def export_success(
    request: Request,
    pdf_url: str = "",
):

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "pdf_url": pdf_url,
        },
    )


@router.get("/test-image")
def test_image(
    request: Request,
    prompt: str = (
        "A friendly young inventor "
        "exploring a colorful futuristic city, "
        "polished comic book illustration, "
        "dynamic composition"
    ),
):

    try:

        image_url = generate_image(
            image_prompt=prompt,
            panel_number=999,
        )

        layout = [
            {
                "panel_number": 1,
                "title": "Image Generation Test",
                "scene_description": (
                    "This is a developer test "
                    "for the image-generation system."
                ),
                "image_prompt": prompt,
                "image_url": image_url,
                "caption": "",
                "narration": "",
                "dialogue": [],
            }
        ]

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "layout": layout,
                "pdf_url": "",
                "story_prompt": "Image generation test",
                "character_name": "Test",
            },
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=_friendly_error(error),
        ) from error


@router.get("/health")
def health_check():

    return {
        "status": "ok",
        "application": "ComicCraftAI",
    }