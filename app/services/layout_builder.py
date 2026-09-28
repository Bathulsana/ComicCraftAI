def build_comic_layout(
    outline: list[dict],
    story: list[dict],
    image_paths: list[str],
) -> list[dict]:

    story_by_number = {
        int(item.get("panel_number", 0)): item
        for item in story
        if isinstance(item, dict)
    }

    layout = []

    for index, panel in enumerate(
        outline,
        start=1,
    ):

        story_item = story_by_number.get(
            index,
            {},
        )

        layout.append(
            {
                "panel_number": index,
                "title": panel.get(
                    "title",
                    f"Panel {index}",
                ),
                "scene_description": panel.get(
                    "scene_description",
                    "",
                ),
                "image_prompt": panel.get(
                    "image_prompt",
                    "",
                ),
                "image_url": image_paths[index - 1],
                "caption": story_item.get(
                    "caption",
                    "",
                ),
                "narration": story_item.get(
                    "narration",
                    "",
                ),
                "dialogue": story_item.get(
                    "dialogue",
                    [],
                ),
            }
        )

    return layout