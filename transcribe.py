import whisper
import tempfile
import os

model = whisper.load_model("base")  # can be "small", "medium", "large"

def transcribe(file, language):

    # create temporary file
    # because whisper expects a file path
    # (need to temporarily save it)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        temp_audio.write(file.read())
        temp_audio_path = temp_audio.name

    options = {}
    if language and language != "Auto":
        options["language"] = language

    result = model.transcribe(temp_audio_path, **options)

    os.remove(temp_audio_path)

    return result["text"]
