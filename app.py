import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    IpBlocked,
)

# Load environment variables from .env file
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# Prompt for Gemini
prompt = """You are a YouTube video summarizer. You will take the transcript text
and summarize the entire video by providing the key points within 250 words. 
Please provide the summary of the text given here: """


# Function to extract transcript from a YouTube URL
def extract_transcript_details(youtube_video_url):
    try:
        # Handle both long and short YouTube URL formats
        if "watch?v=" in youtube_video_url:
            video_id = youtube_video_url.split("watch?v=")[1].split("&")[0]
        elif "youtu.be/" in youtube_video_url:
            video_id = youtube_video_url.split("youtu.be/")[1].split("?")[0]
        else:
            raise ValueError("Invalid YouTube URL format.")

        # Fetch transcript using the video ID
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)

        # Convert transcript list to plain text
        transcript = " ".join([entry["text"] for entry in transcript_text])

        return transcript, video_id

    except IpBlocked:
        st.error("❌ YouTube has blocked your IP. Try using a VPN, proxy, or mobile hotspot.")
    except VideoUnavailable:
        st.error("⚠️ This video is unavailable.")
    except NoTranscriptFound:
        st.warning("⚠️ No transcript found for this video.")
    except TranscriptsDisabled:
        st.warning("⚠️ Transcripts are disabled for this video.")
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")

    return None, None


# Function to generate summary using Gemini
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    response = model.generate_content(prompt + transcript_text)
    return response.text


# Streamlit app UI
st.set_page_config(page_title="YouTube Video Summarizer", layout="centered")
st.title("🎥 YouTube Transcript → ✍️ Detailed Notes Converter")

youtube_link = st.text_input("🔗 Enter YouTube Video Link:")

if youtube_link:
    transcript_text, video_id = extract_transcript_details(youtube_link)

    if video_id:
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)

    if st.button("📝 Get Detailed Notes") and transcript_text:
        with st.spinner("Summarizing video using Gemini..."):
            summary = generate_gemini_content(transcript_text, prompt)
            st.markdown("## 🧾 Detailed Notes:")
            st.write(summary)
