import streamlit as st
from transcribe import transcribe
import re
import html
from rapidfuzz import fuzz
from phrases.phrase_categories import phrase_categories  # <-- import the phrases

st.set_page_config(page_title="Audio/Video Transcriber", layout="centered")
st.title("Whisper Transcription")

uploaded_file = st.file_uploader(
    "Upload an audio or video file",
    type=["mp3", "mp4", "m4a", "wav", "webm"]
)

language_options = [
    "Auto", "English", "Spanish", "French", "German", "Hindi", "Chinese",
    "Japanese", "Korean", "Arabic", "Russian", "Portuguese"
]
selected_language = st.selectbox(
    "Select original language (or choose Auto to detect):", language_options
)

def get_flexible_pattern(phrase):
    # Allow for flexible whitespace, no end boundary
    escaped = re.escape(phrase)
    flexible = re.sub(r'\\ ', r'\\s+', escaped)
    return r'(?<!\w)' + flexible

def highlight_phrases_by_category(text, fuzzy_threshold=80):
    safe_text = html.escape(text)
    phrase_tuples = []
    for cat, data in phrase_categories.items():
        color = data["color"]
        for phrase in data["phrases"]:
            phrase_tuples.append((cat, phrase, color))

    # Sort by phrase length descending for better matching
    phrase_tuples.sort(key=lambda x: len(x[1]), reverse=True)
    highlighted = [False] * len(safe_text)
    spans = []

    # --- REGEX (exact/near-exact) MATCHING ---
    for cat, phrase, color in phrase_tuples:
        pattern = get_flexible_pattern(phrase)
        for match in re.finditer(pattern, safe_text, flags=re.IGNORECASE):
            start, end = match.start(), match.end()
            if not any(highlighted[start:end]):
                spans.append((start, end, color))
                for i in range(start, end):
                    highlighted[i] = True

    # --- FUZZY matching (optional, for inexact cases) ---
    # If you want, you can add fuzzy matching here as in previous examples.

    # Assemble highlighted text
    spans.sort()
    result = []
    last_idx = 0
    for start, end, color in spans:
        if last_idx < start:
            result.append(safe_text[last_idx:start])
        result.append(f'<span style="background-color: {color}; font-weight: bold;">{safe_text[start:end]}</span>')
        last_idx = end
    result.append(safe_text[last_idx:])
    return ''.join(result)

# Build color key HTML for categories (always shown)
color_key_html = '<div style="margin-bottom: 1em; font-family: monospace;">'
color_key_html += '<strong>Color Key:</strong><br>'
for cat, data in phrase_categories.items():
    color = data["color"]
    label = cat.replace('_', ' ').title()
    color_key_html += f'<span style="background-color: {color}; padding: 0.2em 0.6em; margin-right: 1em; border-radius: 4px;">{label}</span>'
color_key_html += '</div>'
st.markdown(color_key_html, unsafe_allow_html=True)

if uploaded_file is not None:
    if st.button("Transcribe"):
        st.audio(uploaded_file, format="audio/mp3")
        with st.spinner("Transcribing... this may take a few seconds depending on the file size"):
            transcription = transcribe(uploaded_file, selected_language)
        st.success("Transcription complete!")

        # Original transcript display
        st.markdown("### 📝 Transcription:")
        st.markdown(f"""
        <style>
        .transcript-box {{
            padding: 1em;
            border-radius: 8px;
            height: 300px;
            overflow-y: auto;
            white-space: pre-wrap;
            font-family: monospace;
        }}
        </style>
        <div class="transcript-box">
        {transcription}
        </div>
        """, unsafe_allow_html=True)

        # Highlighted transcript display
        st.markdown("### 🖍️ Transcription with Categorized Highlights:")
        st.markdown(f"""
        <style>
        .transcript-box-highlight {{
            padding: 1em;
            border-radius: 8px;
            height: 300px;
            overflow-y: auto;
            white-space: pre-wrap;
            font-family: monospace;
        }}
        </style>
        <div class="transcript-box-highlight">
        {highlight_phrases_by_category(transcription)}
        </div>
        """, unsafe_allow_html=True)

        st.download_button(
            label="Download as .txt",
            data=transcription,
            file_name="transcription.txt",
            mime="text/plain"
        )
