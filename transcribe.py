import whisper
import tempfile
import os

# Optionally use a smaller model for speed: "base", "small"
model = whisper.load_model("small")

def transcribe(file, language):
    # Detect extension from uploaded file if possible, fallback to .mp3
    ext = ".mp3"
    if hasattr(file, "name") and "." in file.name:
        ext = os.path.splitext(file.name)[1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_audio:
        temp_audio.write(file.read())
        temp_audio_path = temp_audio.name

    options = {}
    # Map language to ISO code if needed, or ensure UI provides correct codes
    if language and language != "Auto":
        options["language"] = language  # Ensure this matches Whisper's expected codes

    try:
        result = model.transcribe(temp_audio_path, **options)
    finally:
        os.remove(temp_audio_path)

    return result["text"]
