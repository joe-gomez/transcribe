import streamlit as st
from transcribe import transcribe
import re
import html

st.set_page_config(page_title="Audio/Video Transcriber", layout="centered")

st.title("Whisper Transcription")

uploaded_file = st.file_uploader("Upload an audio or video file", type=["mp3", "mp4", "m4a", "wav", "webm"])

language_options = ["Auto", "English", "Spanish", "French", "German", "Hindi", "Chinese", "Japanese", "Korean", "Arabic", "Russian", "Portuguese"]
selected_language = st.selectbox("Select original language (or choose Auto to detect):", language_options)

# ... (phrase_categories stays the same)

def highlight_phrases_by_category(text):
    text = html.escape(text)
    patterns = []
    for cat, data in phrase_categories.items():
        sorted_phrases = sorted(data["phrases"], key=len, reverse=True)
        escaped_phrases = [re.escape(p) for p in sorted_phrases]
        pattern = r'(?P<%s>\b(?:%s)\b)' % (cat, '|'.join(escaped_phrases))
        patterns.append(pattern)
    combined_pattern = '|'.join(patterns)

    def replacer(match):
        for cat in phrase_categories.keys():
            if match.group(cat):
                color = phrase_categories[cat]["color"]
                phrase = match.group(cat)
                return f'<span style="background-color: {color}; font-weight: bold;">{phrase}</span>'
        return match.group(0)
    highlighted = re.sub(combined_pattern, replacer, text, flags=re.IGNORECASE)
    return highlighted

# Build color key HTML for categories (can be outside as it's static)
color_key_html = '<div style="margin-bottom: 1em; font-family: monospace;">'
color_key_html += '<strong>Color Key:</strong><br>'
for cat, data in phrase_categories.items():
    color = data["color"]
    label = cat.replace('_', ' ').title()
    color_key_html += f'<span style="background-color: {color}; padding: 0.2em 0.6em; margin-right: 1em; border-radius: 4px;">{label}</span>'
color_key_html += '</div>'
st.markdown(color_key_html, unsafe_allow_html=True)

# Only process and display UI after transcription happens!
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
