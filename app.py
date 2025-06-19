import streamlit as st
import html
from transcribe import transcribe
from highlight import highlight_phrases_by_category
from phrases.phrase_categories import phrase_categories

st.set_page_config(page_title="Audio/Video Transcriber", layout="centered")
st.title("Video Transcription & Greenwashing Highlighter")

uploaded_file = st.file_uploader(
    "Upload an audio or video file",
    type=["mp3", "mp4", "m4a", "wav", "webm"]
)

language_options = [
    "Auto", "English", "Spanish", "French", "German", "Hindi", "Chinese",
    "Japanese", "Korean", "Arabic", "Russian", "Portuguese"
]
language_code_map = {
    "Auto": None,
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Hindi": "hi",
    "Chinese": "zh",
    "Japanese": "ja",
    "Korean": "ko",
    "Arabic": "ar",
    "Russian": "ru",
    "Portuguese": "pt",
}
selected_language = st.selectbox(
    "Select original language (or choose Auto to detect):", language_options
)
whisper_language = language_code_map[selected_language]

fuzzy_threshold = st.slider(
    "Fuzzy match threshold (lower = more lenient, higher = more strict)",
    min_value=50,
    max_value=100,
    value=80,
    step=1,
    help="Lower values will match phrases more loosely; higher values require closer matches."
)

# --- Show color key ---
color_key_html = '<div style="margin-bottom: 1em; font-family: monospace;">'
color_key_html += '<strong>Color Key:</strong><br>'
for cat, data in phrase_categories.items():
    color = data["color"]
    label = cat.replace('_', ' ').title()
    color_key_html += f'<span style="background-color: {color}; padding: 0.2em 0.6em; margin-right: 1em; border-radius: 4px;">{label}</span>'
color_key_html += '</div>'
st.markdown(color_key_html, unsafe_allow_html=True)

# --- Clear Button for session state ---
if st.button("Clear All / Reset"):
    st.session_state.clear()
    st.experimental_rerun()

# --- Caching transcript ---
@st.cache_data(show_spinner="Transcribing... this may take a few seconds depending on the file size")
def get_transcription(file_bytes, language, file_name):
    return transcribe(file_bytes, language, file_name)

if uploaded_file is not None:
    # Read file ONCE and store bytes and name
    file_bytes = uploaded_file.read()
    file_name = uploaded_file.name

    # Only re-transcribe if file or language changes
    if st.button("Transcribe"):
        try:
            with st.spinner("Transcribing... this may take a few seconds depending on the file size"):
                transcription = get_transcription(file_bytes, whisper_language, file_name)
                st.session_state["transcription"] = transcription
                st.session_state["transcription_file_hash"] = hash(file_bytes)
                st.session_state["transcription_language"] = whisper_language
                st.session_state["transcription_file_name"] = file_name
            st.success("Transcription complete!")
        except Exception as e:
            st.error(f"Transcription failed: {e}")
            transcription = None

    # Display transcript if it exists in session (for re-highlighting)
    elif (
        "transcription" in st.session_state and
        st.session_state.get("transcription_file_hash") == hash(file_bytes) and
        st.session_state.get("transcription_language") == whisper_language and
        st.session_state.get("transcription_file_name") == file_name
    ):
        transcription = st.session_state["transcription"]
        st.success("Transcription loaded from cache!")
    else:
        transcription = None

    if transcription:
        # Smart audio format inference for playback
        audio_ext = file_name.split(".")[-1].lower()
        audio_format = (
            f"audio/mp4" if audio_ext == "m4a"
            else f"audio/{audio_ext}" if audio_ext in ["mp3", "wav", "ogg", "webm"]
            else "audio/mp3"
        )
        st.audio(file_bytes, format=audio_format)

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
        {html.escape(transcription)}
        </div>
        """, unsafe_allow_html=True)

        # Highlighted transcript display
        st.markdown("### 🖍️ Transcription with Categorized Highlights:")
        try:
            highlighted_html = highlight_phrases_by_category(transcription, fuzzy_threshold=fuzzy_threshold)
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
            {highlighted_html}
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Highlighting failed: {e}")

        st.download_button(
            label="Download as .txt",
            data=transcription,
            file_name="transcription.txt",
            mime="text/plain"
        )
    else:
        st.info("Upload a file, select a language, and click Transcribe to begin.")
else:
    st.info("Please upload an audio or video file to get started.")
