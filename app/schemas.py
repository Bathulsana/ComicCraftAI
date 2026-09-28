from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
    story_prompt: str = Field(
        min_length=3,
        max_length=2000,
    )

    character_name: str = Field(
        default="Alex",
        min_length=1,
        max_length=100,
    )

    setting: str = Field(
        default="A modern city",
        min_length=1,
        max_length=200,
    )

    tone: str = Field(
        default="adventurous",
        min_length=1,
        max_length=100,
    )

    art_style: str = Field(
        default="comic book",
        min_length=1,
        max_length=100,
    )