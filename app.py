import streamlit as st
from transcribe import transcribe
import re
import html

st.set_page_config(page_title="Audio/Video Transcriber", layout="centered")

st.title("Whisper Transcription")

uploaded_file = st.file_uploader("Upload an audio or video file", type=["mp3", "mp4", "m4a", "wav", "webm"])

language_options = ["Auto", "English", "Spanish", "French", "German", "Hindi", "Chinese", "Japanese", "Korean", "Arabic", "Russian", "Portuguese"]
selected_language = st.selectbox("Select original language (or choose Auto to detect):", language_options)

def highlight_individualising_language(text):
    phrases = [
        "you should", "your responsibility", "individual choice", "personal duty",
        "you must", "on you", "each person", "it's up to you", "do your part"
    ]
    # Escape HTML entities to prevent injection
    escaped_text = html.escape(text)

    # Create regex pattern with all phrases
    pattern = r'(' + '|'.join(re.escape(p) for p in phrases) + r')'

    # Highlight matched phrases (case insensitive)
    highlighted_text = re.sub(pattern, r'<span class="highlight">\1</span>', escaped_text, flags=re.IGNORECASE)

    return highlighted_text

if uploaded_file is not None and st.button("Transcribe"):
    st.audio(uploaded_file, format="audio/mp3")
    with st.spinner("Transcribing... this may take a few seconds depending on the file size"):
        transcription = transcribe(uploaded_file, selected_language)
    st.success("Transcription complete!")

    # Original transcript display (unchanged)
    st.markdown("### 📝 Transcription:")
    st.markdown("""
    <style>
    .transcript-box {
        padding: 1em;
        border-radius: 8px;
        height: 300px;
        overflow-y: auto;
        white-space: pre-wrap;
        font-family: monospace;
    }
    </style>
    <div class="transcript-box">
    %s
    </div>
    """ % transcription, unsafe_allow_html=True)

    # Highlighted transcript display
    st.markdown("### 🖍️ Transcription with Individualising Language Highlighted:")
    st.markdown("""
    <style>
    .transcript-box-highlight {
        padding: 1em;
        border-radius: 8px;
        height: 300px;
        overflow-y: auto;
        white-space: pre-wrap;
        font-family: monospace;
    }
    .highlight {
        background-color: #fffa65;
        font-weight: bold;
    }
    </style>
    <div class="transcript-box-highlight">
    %s
    </div>
    """ % highlight_individualising_language(transcription), unsafe_allow_html=True)

    st.download_button(
        label="Download as .txt",
        data=transcription,
        file_name="transcription.txt",
        mime="text/plain"
    )
