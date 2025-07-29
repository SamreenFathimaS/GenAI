import streamlit as st
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from youtube_transcript_api import YouTubeTranscriptApi
from langchain.chains import LLMChain
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
import os

# Load OpenAI key from .env file
load_dotenv()

# Initialize OpenAI LLM
llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_Key"),model_name="gpt-4.1",temperature=0.3)

# Create summarization prompt
summary_prompt = PromptTemplate(
    input_variables=["transcript"],
    template="""
You are an expert summarizer.
Here is a video transcript:

{transcript}

Please generate a clear, concise summary of the main points and topics.
"""
)

# Create a LangChain Runnable
summary_chain = LLMChain(llm=llm, prompt=summary_prompt)

# Streamlit UI
st.title("YouTube Video Summarizer")
video_url = st.text_input("Enter YouTube video URL:")

# Extract the video ID safely from URL
def get_video_id(url):
    """
    Extract Video ID from youtube URL

    """

    parsed_url = urlparse(url)
    if parsed_url.hostname == "youtu.be":
        return parsed_url.path[1:]
    elif parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        query = parse_qs(parsed_url.query)
        return query.get('v', [None])[0]
    return None

# When the button is clicked
if st.button("Summarize"):
    if not video_url:
        st.warning("Please enter a video URL.")
    else:
        # Strip extra query strings if needed (e.g., ?si=...)
        video_id = get_video_id(video_url)
        if not video_id:
            st.error("Invalid YouTube URL.")
        else:
            try:
                # Get transcript
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                full_text = " ".join([t['text'] for t in transcript_list])

                # Generate summary using LLM
                summary = summary_chain.run({"transcript": full_text})

                # Display summary
                st.subheader("Video Summary")
                st.write(summary)

            except Exception as e:
                st.error(f"Error: {str(e)}")

