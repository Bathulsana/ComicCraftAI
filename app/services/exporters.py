from datetime import datetime
from pathlib import Path

from fpdf import FPDF

from app.config import BASE_DIR, EXPORTS_DIR


def _pdf_text(value: str) -> str:
    """
    FPDF's standard Helvetica font does not support every Unicode character.
    This converts unsupported characters safely instead of crashing PDF export.
    """
    return (
        str(value or "")
        .encode("latin-1", "replace")
        .decode("latin-1")
    )


def _get_image_path(image_url: str) -> Path:
    relative = image_url.lstrip("/")

    return BASE_DIR / Path(
        *relative.split("/")
    )


def save_pdf(
    layout: list[dict],
) -> str:

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"comic_{timestamp}.pdf"
    )

    output_path = EXPORTS_DIR / filename

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4",
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=12,
    )

    for panel in layout:

        pdf.add_page()

        # Panel title.
        pdf.set_font(
            "Helvetica",
            "B",
            18,
        )

        pdf.cell(
            0,
            10,
            _pdf_text(
                f"Panel {panel['panel_number']}: "
                f"{panel['title']}"
            ),
            ln=True,
        )

        image_path = _get_image_path(
            panel["image_url"]
        )

        current_y = 30

        if image_path.exists():

            pdf.image(
                str(image_path),
                x=10,
                y=28,
                w=190,
                h=110,
                keep_aspect_ratio=True,
            )

            current_y = 142

        pdf.set_y(current_y)

        # Scene description.
        if panel.get("scene_description"):

            pdf.set_font(
                "Helvetica",
                "I",
                11,
            )

            pdf.multi_cell(
                0,
                7,
                _pdf_text(
                    panel["scene_description"]
                ),
            )

        # Caption.
        if panel.get("caption"):

            pdf.ln(2)

            pdf.set_font(
                "Helvetica",
                "B",
                11,
            )

            pdf.multi_cell(
                0,
                6,
                _pdf_text(
                    "Caption: "
                    + panel["caption"]
                ),
            )

        # Narration.
        if panel.get("narration"):

            pdf.ln(1)

            pdf.set_font(
                "Helvetica",
                "",
                11,
            )

            pdf.multi_cell(
                0,
                6,
                _pdf_text(
                    panel["narration"]
                ),
            )

        # Dialogue.
        dialogue = panel.get(
            "dialogue",
            [],
        )

        if dialogue:

            pdf.ln(2)

            pdf.set_font(
                "Helvetica",
                "B",
                11,
            )

            pdf.cell(
                0,
                6,
                "Dialogue",
                ln=True,
            )

            pdf.set_font(
                "Helvetica",
                "",
                10,
            )

            for line in dialogue:

                if not isinstance(
                    line,
                    dict,
                ):
                    continue

                speaker = str(
                    line.get(
                        "speaker",
                        "Character",
                    )
                )

                text = str(
                    line.get(
                        "line",
                        "",
                    )
                )

                pdf.multi_cell(
                    0,
                    5.5,
                    _pdf_text(
                        f"{speaker}: {text}"
                    ),
                )

    pdf.output(
        str(output_path)
    )

    return (
        f"/static/exports/{filename}"
    )