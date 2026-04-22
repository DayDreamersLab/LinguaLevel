# LinguaLevel

LinguaLevel is a Flask app that helps non-native English students adapt material to their CEFR level (A1-C2).

## Features

- Upload `.txt`, `.pdf`, `.docx`, or `.pptx` learning material.
- Select a target CEFR level.
- Simplify vocabulary and sentence complexity to the selected level.
- Download the transformed content in the **same file format** as uploaded.
- Receive a vocabulary list of words/phrases that were simplified, including learner-friendly meanings.

## How simplification works

1. If `OPENAI_API_KEY` is set, the app uses OpenAI to rewrite content to the selected level and return structured vocabulary changes.
2. If no API key is set, a local fallback simplifier replaces a curated set of complex words with simpler alternatives.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app.py
export OPENAI_API_KEY="your-key"  # optional but recommended
flask run
```

Then open http://127.0.0.1:5000.

## Notes

- The output preserves file type, though exact layout/formatting is simplified when rebuilding files.
- PDF and PPTX outputs are regenerated with simplified content and vocabulary section/slide.
