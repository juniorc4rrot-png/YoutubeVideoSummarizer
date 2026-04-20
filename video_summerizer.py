from youtube_transcript_api import YouTubeTranscriptApi
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from urllib.parse import urlparse, parse_qs

# Your Google API Key - Get it from https://aistudio.google.com/app/apikey
GOOGLE_API_KEY = "AIzaSyCJo6SV7Ey5vBkzALAbZ5Anv1hbn6ZqpxY"

def get_video_id(url):
    """Extract video ID from YouTube URL"""
    if 'youtu.be' in url:
        return url.split('/')[-1].split('?')[0]
    elif 'youtube.com' in url:
        parsed = urlparse(url)
        video_id = parse_qs(parsed.query).get('v', [None])[0]
        return video_id
    return None

def get_transcript(video_id):
    """Get transcript from YouTube video"""
    try:
        # Create API instance and fetch transcript
        api = YouTubeTranscriptApi()
        transcript_data = api.fetch(video_id, languages=['en'])
        
        # Combine all transcript segments into one text
        # transcript_data is iterable, each item has .text attribute
        full_text = " ".join([entry.text for entry in transcript_data])
        
        return full_text, len(full_text.split())
    
    except Exception as e:
        print(f"✗ Error: Could not fetch transcript - {e}")
        print("  Note: This video may not have English captions available.")
        return None, 0

def generate_summary(transcript_text, video_url):
    """Generate summary using Gemini"""
    
    # Create prompt
    prompt = f"""Summarize this YouTube video transcript in a clear, structured format.

Video URL: {video_url}

Transcript:
{transcript_text}

Provide:
1. A concise 2-3 paragraph summary of the main content
2. Key topics covered (as bullet points)
3. Main takeaways (as a numbered list)
4. Whether the video is worth watching and for whom

Keep it concise but informative. Use clear headings and formatting."""
    
    # Initialize Gemini
    llm = ChatGoogleGenerativeAI(
        model='gemini-3-flash-preview',
        google_api_key=GOOGLE_API_KEY
    )
    
    # Get response
    response = llm.invoke([HumanMessage(content=prompt)])
    
    # Extract text
    summary = response.content[0]['text']
    
    return summary

def main():
    print("YouTube Video Summarizer")
    print("========================\n")
    
    # Get YouTube URL
    url = input("Enter YouTube URL: ").strip()
    
    # Extract video ID
    video_id = get_video_id(url)
    
    if not video_id:
        print("✗ Error: Invalid YouTube URL")
        return
    
    print("\nFetching video information...")
    
    # Get transcript
    transcript_text, word_count = get_transcript(video_id)
    
    if not transcript_text:
        return
    
    print(f"✓ Video ID: {video_id}")
    print(f"✓ Transcript: {word_count:,} words")
    
    # Generate summary
    print("\nGenerating summary...")
    
    summary = generate_summary(transcript_text, url)
    
    # Display summary
    print("\n" + "="*60)
    print("📺 VIDEO SUMMARY")
    print("="*60 + "\n")
    print(summary)
    print("\n" + "="*60)
    print("✓ Summary complete!")

if __name__ == "__main__":
    main()