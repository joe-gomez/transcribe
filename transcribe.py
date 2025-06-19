import whisper
import tempfile
import os

model = whisper.load_model("small")  # or "base"

def transcribe(file_bytes, language, original_name="audio.mp3"):
    ext = os.path.splitext(original_name)[1].lower() if "." in original_name else ".mp3"
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_audio:
        temp_audio.write(file_bytes)
        temp_audio_path = temp_audio.name

    options = {}
    if language and language != "Auto":
        options["language"] = language  # Should be ISO code, e.g. "en"

    try:
        result = model.transcribe(temp_audio_path, **options)
    finally:
        os.remove(temp_audio_path)

    return result["text"]
