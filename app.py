# Greenwashing-Detector-App.py
import streamlit as st
from transcribe import transcribe
from highlight import highlight_greenwashing_strategies
import re

st.set_page_config(
    page_title="Greenwashing Detector", 
    layout="wide",
    page_icon="🌱"
)

st.title("🌱 Greenwashing Detector")
st.markdown("*Analyze audio/video content for rhetorical strategies commonly used in greenwashing*")

# Sidebar with information
with st.sidebar:
    st.header("About Greenwashing Strategies")
    st.markdown("""
    **🔵 Collective 'We'**  
    Vague shared responsibility, no real actor
    
    **🟡 Individualising Language**  
    "You can do your part" - personal responsibility
    
    **🔴 Moral Metaphors**  
    "Journey," "mission," "battle" language
    
    **🟢 Green Buzzwords**  
    "Planet," "recycle," "responsible," "sustainable"
    """)

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📁 Upload Content")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload an audio or video file", 
        type=["mp3", "mp4", "m4a", "wav", "webm"]
    )
    
    # Language selection
    language_options = [
        "Auto", "English", "Spanish", "French", "German", 
        "Hindi", "Chinese", "Japanese", "Korean", "Arabic", 
        "Russian", "Portuguese"
    ]
    selected_language = st.selectbox(
        "Select original language:", 
        language_options
    )
    
    # Text input alternative
    st.markdown("**Or paste text directly:**")
    text_input = st.text_area(
        "Enter text to analyze:",
        height=150,
        placeholder="Paste advertisement text, speech transcript, or marketing copy here..."
    )

with col2:
    st.subheader("⚙️ Analysis Settings")
    
    # Sensitivity settings
    sensitivity = st.slider(
        "Detection Sensitivity",
        min_value=1,
        max_value=3,
        value=2,
        help="1 = Strict matches only, 2 = Moderate, 3 = Broad pattern matching"
    )
    
    # Strategy selection
    st.markdown("**Select strategies to detect:**")
    detect_collective = st.checkbox("🔵 Collective 'We'", value=True)
    detect_individual = st.checkbox("🟡 Individualising Language", value=True)
    detect_metaphors = st.checkbox("🔴 Moral Metaphors", value=True)
    detect_buzzwords = st.checkbox("🟢 Green Buzzwords", value=True)

# Process content
transcription = ""
if uploaded_file is not None and st.button("🎧 Transcribe and Analyze"):
    with st.spinner("Transcribing... this may take a few moments"):
        transcription = transcribe(uploaded_file, selected_language)
    st.success("Transcription complete!")

elif text_input and st.button("🔍 Analyze Text"):
    transcription = text_input
    st.success("Text loaded for analysis!")

# Analysis results
if transcription:
    st.markdown("---")
    st.subheader("📊 Analysis Results")
    
    # Get highlighted text and statistics
    highlighted_text, stats = highlight_greenwashing_strategies(
        transcription, 
        sensitivity,
        detect_collective,
        detect_individual, 
        detect_metaphors,
        detect_buzzwords
    )
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🔵 Collective 'We'", stats['collective'])
    with col2:
        st.metric("🟡 Individual Language", stats['individual'])
    with col3:
        st.metric("🔴 Moral Metaphors", stats['metaphors'])
    with col4:
        st.metric("🟢 Green Buzzwords", stats['buzzwords'])
    
    # Overall assessment
    total_matches = sum(stats.values())
    if total_matches > 10:
        assessment = "🚨 High greenwashing indicators detected"
        color = "#ff4444"
    elif total_matches > 5:
        assessment = "⚠️ Moderate greenwashing indicators"
        color = "#ffaa00"
    elif total_matches > 0:
        assessment = "✅ Some indicators present"
        color = "#44aa44"
    else:
        assessment = "✅ No significant indicators detected"
        color = "#44aa44"
    
    st.markdown(f"""
    <div style="padding: 1rem; border-radius: 0.5rem; background-color: {color}20; border-left: 4px solid {color};">
        <h4 style="color: {color}; margin: 0;">{assessment}</h4>
        <p style="margin: 0.5rem 0 0 0;">Total indicators found: {total_matches}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display highlighted text
    st.subheader("📝 Highlighted Text")
    st.markdown("""
    <style>
    .transcript-box {
        padding: 1.5rem;
        border-radius: 8px;
        max-height: 400px;
        overflow-y: auto;
        white-space: pre-wrap;
        font-family: 'Georgia', serif;
        line-height: 1.6;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
    }
    .collective-we {
        background-color: #3498db;
        color: white;
        padding: 2px 4px;
        border-radius: 3px;
        font-weight: bold;
    }
    .individualising {
        background-color: #f1c40f;
        color: #2c3e50;
        padding: 2px 4px;
        border-radius: 3px;
        font-weight: bold;
    }
    .moral-metaphors {
        background-color: #e74c3c;
        color: white;
        padding: 2px 4px;
        border-radius: 3px;
        font-weight: bold;
    }
    .green-buzzwords {
        background-color: #27ae60;
        color: white;
        padding: 2px 4px;
        border-radius: 3px;
        font-weight: bold;
    }
    </style>
    <div class="transcript-box">
    %s
    </div>
    """ % highlighted_text, unsafe_allow_html=True)
    
    # Download options
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📄 Download Transcript",
            data=transcription,
            file_name="transcript.txt",
            mime="text/plain"
        )
    with col2:
        # Create analysis report
        report = f"""Greenwashing Analysis Report
=============================

Text analyzed: {len(transcription)} characters

Strategy Detection Results:
- Collective 'We': {stats['collective']} instances
- Individualising Language: {stats['individual']} instances  
- Moral Metaphors: {stats['metaphors']} instances
- Green Buzzwords: {stats['buzzwords']} instances

Overall Assessment: {assessment}
Total Indicators: {total_matches}

Original Text:
{transcription}
"""
        st.download_button(
            label="📊 Download Analysis Report",
            data=report,
            file_name="greenwashing_analysis.txt",
            mime="text/plain"
        )
