import os
from dotenv import load_dotenv
import requests
from murf import Murf

# Load .env file
load_dotenv()
MURF_API_KEY = os.getenv("MURF_API_KEY")

if not MURF_API_KEY:
    raise ValueError("MURF_API_KEY not found in .env file")

# Paths
script_dir = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.join(script_dir, "..", "..", "app", "outputs", "motivational_script.md")
output_mp3 = os.path.join(script_dir, "..", "..", "app", "outputs", "podcast.mp3")

def read_markdown(md_file_path: str) -> str:
    """Reads a Markdown file and returns its content as plain text"""
    with open(md_file_path, "r", encoding="utf-8") as f:
        return f.read()

def save_to_file(text: str, voice_id: str, file_path: str):
    """Generates speech using Murf SDK and saves it locally"""
    client = Murf(api_key=MURF_API_KEY)
    
    # Generate audio
    res = client.text_to_speech.generate(
        text=text,
        voice_id=voice_id
    )
    
    url_to_audio_file = res.audio_file
    audio_file = requests.get(url_to_audio_file)
    
    if audio_file.status_code == 200:
        with open(file_path, 'wb') as f:
            f.write(audio_file.content)
        print(f"🎧 Podcast saved at: {file_path}")
    else:
        print(f"❌ Failed to download audio. Status code: {audio_file.status_code}")

def run_pipeline_murf(md_file_path=None, audio_output_path=None, voice_id="en-US-charles") -> str:
    """
    Full pipeline: read Markdown → convert to audio → return path to MP3
    If paths are None, defaults to app/outputs folder.
    """
    script_dir = os.path.dirname(__file__)
    outputs_dir = os.path.join(script_dir, "..", "..", "app", "outputs")
    os.makedirs(outputs_dir, exist_ok=True)

    if md_file_path is None:
        md_file_path = os.path.join(outputs_dir, "motivational_script.md")
    if audio_output_path is None:
        audio_output_path = os.path.join(outputs_dir, "podcast.mp3")

    script_text = read_markdown(md_file_path)
    save_to_file(script_text, voice_id=voice_id, file_path=audio_output_path)

    return audio_output_path

if __name__ == "__main__":
    script_text = read_markdown(script_path)
    save_to_file(script_text, voice_id="en-US-charles", file_path=output_mp3)
