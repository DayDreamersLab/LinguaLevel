from flask import Flask, render_template, request, send_file, flash
from io import BytesIO
import os

from file_processors import (
    SUPPORTED_EXTENSIONS,
    extract_text,
    rebuild_file,
)
from simplifier import simplify_text

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        level = request.form.get("level", "").upper()
        upload = request.files.get("material")

        if level not in {"A1", "A2", "B1", "B2", "C1", "C2"}:
            flash("Please select a valid CEFR level.")
            return render_template("index.html")

        if not upload or upload.filename == "":
            flash("Please upload a file.")
            return render_template("index.html")

        ext = os.path.splitext(upload.filename)[1].lower()
        if ext not in SUPPORTED_EXTENSIONS:
            flash(f"Unsupported file type: {ext}")
            return render_template("index.html")

        original_text = extract_text(upload.stream, ext)
        simplified_text, vocab_changes = simplify_text(original_text, level)
        output_stream, output_name = rebuild_file(
            original_filename=upload.filename,
            extension=ext,
            simplified_text=simplified_text,
            target_level=level,
            vocab_changes=vocab_changes,
        )

        return send_file(
            output_stream,
            as_attachment=True,
            download_name=output_name,
            mimetype="application/octet-stream",
        )

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
