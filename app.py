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
            "you", "you're", "your", "yours", "yourself", "yourselves",
            "you should", "you must", "you have to", "you need to", "you can",
            "you could", "you might", "you may", "you ought to", "you'd better",
            "you are expected to", "you're expected to", "you are required to", "you're required to",
            "your responsibility", "your duty", "your job", "it's on you",
            "each of you", "every one of you", "everybody should", "everyone must",
            "do your part", "do your bit", "do your share", "make a difference yourself",
            "one person at a time", "it starts with you", "take action", "take responsibility",
            "individual action", "individual responsibility", "personal action", "personal responsibility"
        ],
    },
    "collective_we": {
        "color": "#8ad6ff",  # light blue
        "phrases": [
            "we", "we're", "we are", "our", "ours", "ourselves",
            "we should", "we must", "we have to", "we need to", "we can", "we could", "we might", "we may",
            "we ought to", "we'd better", "we are expected to", "we're expected to", "we are required to", "we're required to",
            "we all", "all of us", "let's", "let us", "together we", "as a community", "as a society", "as a nation", "as a planet",
            "we're messing up", "we're ruining", "we're destroying", "we're failing", "we need to change", "we have to act", "we should try",
            "we think it's time", "we can do better", "we need to do better", "we need to act", "we must act", "we must try", "we must change",
            "we're looking after", "we're taking care of", "we can fix", "we're fixing up", "fixing up the planet", "fixing up real good"
        ],
    },
    "greenwashing": {
        "color": "#b0ffb0",  # light green
        "phrases": [
            "natural", "nature's", "nature", "healthy", "healthier planet", "sustainable", "eco-friendly", "eco friendly",
            "green", "clean", "fresh", "pure", "safe", "responsible", "better for the planet", "planet-friendly", "environmentally friendly",
            "kind to the planet", "planet safe", "planet care", "earth safe", "earth care", "earth friendly", "tread lightly",
            "gentle on the earth", "gentle on the planet", "planet positive", "earth positive", "climate positive", "climate neutral",
            "net zero", "carbon neutral", "carbon negative", "offset", "offsetting", "carbon offset", "climate compensated",
            "innocent", "little drinks", "big dreams", "big dreams for a healthier planet", "innocent little drinks with big dreams"
        ],
    },
    "moral_metaphors": {
        "color": "#ffb0b0",  # light red/pink
        "phrases": [
            "no planet b", "there is no planet b", "mother nature", "mother earth", "earth is hurting", "planet is hurting",
            "earth is crying", "planet is crying", "save our home", "save the earth", "save the planet", "look after nature",
            "look after the earth", "look after the planet", "planet b", "earth is our home", "our only home", "protect our home",
            "the planet is our home", "if we look after nature she'll be looking after me", "nature will look after us",
            "impending doom", "doom and gloom", "dire consequences", "the end is near"
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
