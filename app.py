import streamlit as st
import html
from transcribe import transcribe
from highlight import highlight_phrases_by_category
from phrases.phrase_categories import phrase_categories

st.set_page_config(page_title="Audio/Video Transcriber", layout="centered")
st.title("Whisper Transcription & Phrase Highlighter")

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

# --- Caching transcript ---
@st.cache_data(show_spinner="Transcribing... this may take a few seconds depending on the file size")
def get_transcription(file_bytes, language, file_name):
    import io
    file_obj = io.BytesIO(file_bytes)
    file_obj.name = file_name
    return transcribe(file_obj, language)

if uploaded_file is not None:
    # Read file ONCE and store bytes and name
    file_bytes = uploaded_file.read()
    file_name = uploaded_file.name

    # Only re-transcribe if file or language changes
    if st.button("Transcribe"):
        with st.spinner("Transcribing... this may take a few seconds depending on the file size"):
            transcription = get_transcription(file_bytes, selected_language, file_name)
            st.session_state["transcription"] = transcription
            st.session_state["transcription_file_hash"] = hash(file_bytes)
            st.session_state["transcription_language"] = selected_language
            st.session_state["transcription_file_name"] = file_name
        st.success("Transcription complete!")

    # Display transcript if it exists in session (for re-highlighting)
    elif (
        "transcription" in st.session_state and
        st.session_state.get("transcription_file_hash") == hash(file_bytes) and
        st.session_state.get("transcription_language") == selected_language and
        st.session_state.get("transcription_file_name") == file_name
    ):
        transcription = st.session_state["transcription"]
        st.success("Transcription loaded from cache!")
    else:
        transcription = None

    if transcription:
        st.audio(file_bytes, format="audio/mp3")

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
        {highlight_phrases_by_category(transcription, fuzzy_threshold=fuzzy_threshold)}
        </div>
        """, unsafe_allow_html=True)

        st.download_button(
            label="Download as .txt",
            data=transcription,
            file_name="transcription.txt",
            mime="text/plain"
        )
