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
        "you've", "you'll", "you'd", "should"
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
        "it starts with you", "lead by example", "manage your impact", "control your behavior", "watch your habits", "reduce your footprint",
        "live responsibly", "live sustainably", "choose better", "choose wisely", "choose green",
        "think before you", "be mindful of your", "change your lifestyle", "alter your behavior",
        "cut your emissions", "cut your waste", "minimize your impact", "track your carbon",
        "monitor your consumption", "limit your usage", "reconsider your habits",
        "hold yourself to account", "be part of the solution", "change starts with you",
        "start with yourself", "fix your mindset", "make better choices", "it's on you",
        "every decision you make", "be aware of your", "you're the problem", "be the change",
        "it's your problem", "solve it yourself", "self-improvement", "responsible living",
        "personal action", "personal impact", "your sustainability journey",
        "greener choices", "make the right choice", "shift your mindset", "your ethical duty",
        "align your values", "own your journey", "commit to change", "your moral duty",
        "choose to act", "make a conscious choice", "develop good habits",
        "clean up your act", "consider your actions", "change your ways", "learn to be better",
        "develop sustainable habits", "improve your footprint", "be responsible",
        "align your behavior", "correct your path", "take initiative", "be more aware",
        "self-discipline", "cultivate awareness", "you are part of the problem", "you are the solution",
        "your decisions matter", "your lifestyle choices", "reflect on your impact",
        "you control the future", "your behaviour counts", "lead the change", "take initiative" 
        
          # Direct second-person responsibility
        "you", "you're", "your", "yours", "yourself", "yourselves",
        "you've", "you'll", "you'd",   
        "you should", "you must", "you have to", "you need to", "you can",
        "you could", "you might", "you may", "you ought to", "you'd better",
        "you are expected to", "you're expected to", "you are required to",
        "you're required to", "you are responsible for", "you're responsible for",
        "your responsibility", "your duty", "your obligation", "your role",
        "your job", "your task", "your effort", "your part",
        "take responsibility", "take charge", "take control", "own your actions",
        "bear the responsibility", "accept responsibility", "shoulder the responsibility",
        "carry the burden", "do your part", "play your role", "do your duty",
        "do your job", "make your choice", "make your decision",
        "make the effort", "meet your obligations", "fulfill your responsibilities",
        "if you want to", "if you choose to", "it's up to you",
        "depends on you", "rely on you", "rest on you", "on your shoulders",
        "you have a duty to", "you have a responsibility to", "you owe it to",
        "you must do your part", "you should do your part", "do your best",
        "do what you can", "play your part", "step up",
        "it’s your responsibility", "it’s your choice", "it’s up to you",
        "on you to", "your role in", "your part in", "your contribution",
        "you're responsible", "you are responsible", "you're obliged", "you are obliged",
        "you're accountable", "you are accountable", "hold yourself accountable",
        "take ownership", "own it", "own your impact",
        "accept the consequences", "face the consequences", "answer for",
        "you can make a difference", "you have the power", "you hold the key",
        "you decide", "you choose", "it's your call",
        "you must act", "you should act", "you have to act", "you need to act",
        "you can help", "you can change", "you must change", "you should change",
        "it starts with you", "lead by example",
    
        # First-person collective ("we") individualising
        "we're messing up", "we're ruining", "we're destroying", "we're failing",
        "we need to change", "we have to act", "we should try", "we must",
        "let's fix it", "let’s change", "let’s get fixing", "we can do better",
        "we're all responsible", "we all need to do our bit", "we’re to blame",
        "we’re part of the problem", "we’re part of the solution", "our duty",
        "our responsibility", "our fault", "we've got to", "we’ve been bad",
        "we must do better", "we should do better", "our role", "our job",
        "each of us must", "each one of us should", "we must act now",
    
        # Soft or poetic euphemisms
        "be kinder to", "do our bit", "do the right thing", "clean up our act",
        "fix it up", "tidy up the planet", "play your part", "make better choices",
        "nature’s tasty food", "little things make a big difference",
        "big dreams for a healthier planet", "small steps matter",
        "every action counts", "start with small changes", "change begins with you",
        "change begins with us", "change starts here", "better choices every day",
        "for a better tomorrow", "plant the seed of change", "build a better world",
        "choose better", "choose wisely", "positive actions", "be a hero",
        "make it better", "help change the world", "help fix the planet",
        "help protect the planet", "save the earth", "care more",
    
        # Anthropomorphised environmental moral metaphors
        "no planet B", "the planet needs us", "protect her", "heal the earth",
        "save our home", "look after nature", "look after the earth",
        "if we look after nature", "she’ll be looking after me",
        "mother nature", "mother earth", "earth is hurting",
        "nature will thank us", "nature is watching", "nature is calling",
        "planet is crying", "planet is watching", "earth depends on you",
        "earth is in your hands", "care for the planet", "earth is suffering",
        "planet is our home", "nature needs you", "live in harmony with nature",
        "respect nature", "nurture the planet", "earth is counting on you",
    
        # Ambiguous shared/individual slogans (often greenwashed)
        "every little helps", "think before you", "be the change",
        "responsibility starts here", "lead the way", "it’s the right thing to do",
        "it starts with one", "one action at a time", "your impact matters",
        "your choices count", "live sustainably", "choose the planet",
        "go green", "act now", "take climate action", "join the movement"

            greenwashing_individualising_phrases = [
        # Individualising / blame-shifting phrases
        "you should", "your responsibility", "you must", "you have to", "you need to", "it's up to you",
        "do your part", "play your role", "take responsibility", "personal duty", "individual choice",
        "your obligation", "your role", "your job", "your effort", "your part",
        "it's your responsibility", "you are responsible", "you're responsible",
        "shoulder the responsibility", "carry the burden", "accept responsibility",
        "make the effort", "meet your obligations", "fulfill your responsibilities",
        "you owe it to", "you have a duty to", "it's your call", "you decide", "you choose",
        "own your actions", "own it", "hold yourself accountable", "take ownership",
        "do your best", "do what you can", "step up", "lead by example",
        
        # Greenwashing buzzwords / vague positive framing
        "natural", "nature's", "healthy", "healthier planet", "sustainable", "eco-friendly",
        "green", "clean", "fresh", "pure", "safe", "responsible", "big dreams",
        "little drinks", "better choice", "good for you", "feel good", "better for the planet",
        "reuse", "recycle", "reduce", "protect nature", "looking after nature",
        "planet B", "saving the planet", "fixing up the planet", "fix it up real good",
        "kind to our bodies", "looking after me", "big dreams for a healthier planet",
        
        # Phrases that can imply deflection or vague commitment
        "let's try this instead", "okay", "we're messing up real good", "what are we doing",
        "singing a song about our impending doom", "egging them on", "I know",
        "there is no planet B", "if we're looking after nature", "she'll be looking after me"
  
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
