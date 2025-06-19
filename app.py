import streamlit as st
from transcribe import transcribe
import re
import html

st.set_page_config(page_title="Audio/Video Transcriber", layout="centered")

st.title("Whisper Transcription")

uploaded_file = st.file_uploader("Upload an audio or video file", type=["mp3", "mp4", "m4a", "wav", "webm"])

language_options = ["Auto", "English", "Spanish", "French", "German", "Hindi", "Chinese", "Japanese", "Korean", "Arabic", "Russian", "Portuguese"]
selected_language = st.selectbox("Select original language (or choose Auto to detect):", language_options)

import re
import html

def highlight_individualising_language(text):
    phrases = [
        "you", "you're", "your", "yours", "yourself", "yourselves",
        "you've", "you'll", "you'd",
        "you should", "you must", "you have to", "you need to", "you can",
        "you could", "you might", "you may", "you ought to", "you'd better",
        "you are expected to", "you're expected to", "you are required to",
        "you're required to", "you are responsible for", "you're responsible for",
        "your responsibility", "your duty", "your obligation", "your role",
        "your job", "your task", "your effort", "your part",
        "personal responsibility", "personal duty", "personal obligation",
        "individual responsibility", "individual duty", "individual obligation",
        "own responsibility", "own duty", "own obligation", "own role",
        "take responsibility", "take charge", "take control", "own your actions",
        "bear the responsibility", "accept responsibility", "shoulder the responsibility",
        "carry the burden", "do your part", "play your role", "do your duty",
        "do your job", "make your choice", "make your decision",
        "make the effort", "meet your obligations", "fulfill your responsibilities",
        "if you want to", "if you choose to", "it's up to you",
        "depends on you", "rely on you", "rest on you", "on your shoulders",
        "each person", "every person", "each individual", "every individual",
        "each of us", "every one of us", "all of us", "everyone must",
        "everyone should", "everyone has to", "everyone needs to",
        "everybody should", "everybody must", "everybody has to",
        "you have a duty to", "you have a responsibility to", "you owe it to",
        "you must do your part", "you should do your part", "do your best",
        "do what you can", "play your part", "step up",
        "it’s your responsibility", "it’s your choice", "it’s up to you",
        "on you to", "your role in", "your part in", "your contribution",
        "you're responsible", "you are responsible", "you're obliged", "you are obliged",
        "you're expected to", "you are expected to", "you're accountable", "you are accountable",
        "hold yourself accountable", "take ownership", "own it",
        "accept the consequences", "face the consequences", "answer for",
        "you can make a difference", "you have the power", "you hold the key",
        "you decide", "you choose", "it's your call",
        "you must act", "you should act", "you have to act", "you need to act",
        "you can help", "you can change", "you must change", "you should change",
        "it starts with you", "lead by example"
    ]

    # Escape HTML to prevent injection
    text = html.escape(text)

    # Build a regex pattern that matches any phrase (with word boundaries)
    # Sort by length to avoid partial matching inside longer phrases
    phrases_sorted = sorted(phrases, key=len, reverse=True)
    pattern = r'\b(' + '|'.join(re.escape(p) for p in phrases_sorted) + r')\b'

    # Use re.IGNORECASE for case-insensitive matching
    highlighted = re.sub(pattern, r'<span class="highlight">\1</span>', text, flags=re.IGNORECASE)

    return highlighted


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
