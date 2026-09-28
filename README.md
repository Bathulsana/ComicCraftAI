# 🎨 ComicCraftAI

## AI-Powered Comic Story Creator

ComicCraftAI is a web-based AI application that transforms a user's
creative idea into a complete five-panel comic.

The application combines AI-generated storytelling, character dialogue,
scene descriptions, comic-style illustrations, and PDF export into one
simple workflow.

---

## ✨ What ComicCraftAI Does

A user provides:

- Story Prompt
- Main Character Name
- Setting
- Story Tone
- Art Style

ComicCraftAI then:

1. Generates a structured five-panel comic outline.
2. Creates narration, captions, and character dialogue.
3. Generates an illustration for each panel.
4. Combines the text and images into a comic layout.
5. Displays the completed comic in the browser.
6. Exports the comic as a downloadable PDF.

---

## 🚀 Key Features

- 🤖 AI-powered story generation
- 📖 Five-panel comic structure
- 💬 Character dialogue and narration
- 🖼️ AI-generated comic illustrations
- 🎭 Custom story tone and art style
- 👤 Custom main character
- 🌍 Custom story setting
- 👀 Panel-by-panel comic preview
- 📄 PDF comic export
- 🔌 JSON API endpoint
- 🧪 Image-generation test endpoint
- ⚡ FastAPI backend
- 🎨 Jinja2-based web interface

---

## 🏗️ Project Architecture

ComicCraftAI is organized into three major layers:

### Frontend

- HTML
- CSS
- Jinja2 templates

### Backend

- FastAPI
- Pydantic
- Routing and validation
- Error handling

### AI Services

- Gemini for comic outline and story generation
- Hugging Face hosted image inference for illustrations
- Gemini image generation as an image-generation fallback

---

## 📂 Project Structure

```text
ComicCraftAI/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   ├── routes.py
│   ├── schemas.py
│   │
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── gemini_flash.py
│   │   └── gemini_pro.py
│   │
│   └── services/
│       ├── __init__.py
│       ├── comic_service.py
│       ├── exporters.py
│       ├── image_generator.py
│       └── layout_builder.py
│
├── static/
│   ├── exports/
│   └── panels/
│
├── templates/
│   ├── index.html
│   ├── comic_preview.html
│   └── export_success.html
│
├── .env
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt