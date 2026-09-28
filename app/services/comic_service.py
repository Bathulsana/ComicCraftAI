from app.ai.gemini_flash import generate_outline
from app.ai.gemini_pro import generate_story
from app.services.exporters import save_pdf
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout


def generate_comic(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> dict:

    # Step 1:
    # Generate a structured five-panel outline.
    outline = generate_outline(
        story_prompt=story_prompt,
        character_name=character_name,
        setting=setting,
        tone=tone,
        art_style=art_style,
    )

    # Step 2:
    # Generate narration, captions and dialogue.
    story = generate_story(
        outline
    )

    # Step 3:
    # Generate one illustration for each panel.
    image_paths = []

    for panel in outline:

        image_path = generate_image(
            image_prompt=panel["image_prompt"],
            panel_number=panel["panel_number"],
        )

        image_paths.append(
            image_path
        )

    # Step 4:
    # Combine text and images into a structured layout.
    layout = build_comic_layout(
        outline=outline,
        story=story,
        image_paths=image_paths,
    )

    # Step 5:
    # Export the complete comic as PDF.
    pdf_url = save_pdf(
        layout
    )

    return {
        "layout": layout,
        "pdf_url": pdf_url,
        "story_prompt": story_prompt,
        "character_name": character_name,
        "setting": setting,
        "tone": tone,
        "art_style": art_style,
    }