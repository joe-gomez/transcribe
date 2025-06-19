import streamlit as st
from transcribe import transcribe
import re
import html
from rapidfuzz import fuzz, process

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

# Define phrase categories and their associated colors
phrase_categories = {
    "individualising": {
        "color": "#fffa65",  # yellow
        "phrases": [
            # ... (same as before, omitted for brevity)
            "you", "you're", "your", "yours", "yourself", "yourselves", "you should", "you must", "you have to", "you need to", "you can",
            "you could", "you might", "you may", "you ought to", "you'd better", "you are expected to", "you're expected to", "you are required to",
            "you're required to", # ... list continues ...
        ],
    },
    "collective_we": {
        "color": "#8ad6ff",  # light blue
        "phrases": [
            # ... (same as before, omitted for brevity)
            "we're messing up", "we're ruining", "we're destroying", "we're failing", "we need to change", "we have to act", "we should try", "we must",
            # ... list continues ...
        ],
    },
    "greenwashing": {
        "color": "#b0ffb0",  # light green
        "phrases": [
            # ... (same as before, omitted for brevity)
            "natural", "nature's", "healthy", "healthier planet", "sustainable", "eco-friendly", "green", "clean", "fresh", "pure", "safe", "responsible",
            # ... list continues ...
        ],
    },
    "moral_metaphors": {
        "color": "#ffb0b0",  # light red/pink
        "phrases": [
            # ... (same as before, omitted for brevity)
            "no planet B", "mother nature", "mother earth", "earth is hurting", "planet is crying", "save our home", "look after nature",
            # ... list continues ...
        ],
    }
}

def get_flexible_pattern(phrase):
    """
    Returns a regex pattern for a phrase that allows for leading/trailing punctuation and whitespace.
    """
    # Escape regex metacharacters in phrase, but allow spaces.
    escaped = re.escape(phrase)
    # Replace escaped spaces with \s+ to allow flexible whitespace between words
    flexible = re.sub(r'\\ ', r'\\s+', escaped)
    # Allow leading/trailing punctuation or start/end of string
    # (?<!\w) at the start means: not preceded by a word character
    # (?!\w) at the end means: not followed by a word character
    return r'(?<!\w)'+flexible+r'(?!\w)'

def highlight_phrases_by_category(text, fuzzy_threshold=90):
    """
    Highlights phrases from categories in the text using flexible matching and fuzzy matching for near-matches.
    """
    # Escape HTML to prevent injection
    safe_text = html.escape(text)

    # Build a list of (category, phrase, color) for all phrases
    phrase_tuples = []
    for cat, data in phrase_categories.items():
        color = data["color"]
        for phrase in data["phrases"]:
            phrase_tuples.append((cat, phrase, color))

    # Sort by phrase length descending (to match longest possible first)
    phrase_tuples.sort(key=lambda x: len(x[1]), reverse=True)

    # Track which character indices have been highlighted to prevent overlaps
    highlighted = [False] * len(safe_text)
    spans = []

    # Standardize text for fuzzy search (lowercase, normalize whitespace)
    standardized_text = re.sub(r'\s+', ' ', safe_text.lower())

    for cat, phrase, color in phrase_tuples:
        # Flexible regex pattern for the phrase
        pattern = get_flexible_pattern(phrase)
        for match in re.finditer(pattern, safe_text, flags=re.IGNORECASE):
            start, end = match.start(), match.end()
            # Only highlight if this region isn't already highlighted
            if not any(highlighted[start:end]):
                spans.append((start, end, color))
                for i in range(start, end):
                    highlighted[i] = True

        # Fuzzy matching: look for approximate phrase matches in sliding windows
        words = phrase.split()
        num_words = len(words)
        if num_words < 2:
            continue  # Skip fuzzy for single-word phrases (too many false positives)

        # Slide window over the text for fuzzy matching
        tokens = standardized_text.split()
        for i in range(len(tokens) - num_words + 1):
            window = ' '.join(tokens[i:i+num_words])
            score = fuzz.ratio(window, phrase.lower())
            if score >= fuzzy_threshold:
                # Find this window in the original safe_text (best effort)
                raw_window = ' '.join(tokens[i:i+num_words])
                match_iter = re.finditer(re.escape(raw_window), safe_text, re.IGNORECASE)
                for m in match_iter:
                    start, end = m.start(), m.end()
                    if not any(highlighted[start:end]):
                        spans.append((start, end, color))
                        for j in range(start, end):
                            highlighted[j] = True
                        break  # Only highlight the first occurrence

    # Merge and sort spans, and build highlighted HTML
    spans.sort()
    result = []
    last_idx = 0
    for start, end, color in spans:
        if last_idx < start:
            result.append(safe_text[last_idx:start])
        phrase_html = f'<span style="background-color: {color}; font-weight: bold;">{safe_text[start:end]}</span>'
        result.append(phrase_html)
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
