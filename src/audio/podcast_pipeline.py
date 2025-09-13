import os
from gtts import gTTS

def read_markdown(md_file_path: str) -> str:
    """
    Reads a Markdown file and returns the text without headers.
    """
    with open(md_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove Markdown header if present
    if content.startswith("# Motivational Script"):
        content = content.split("\n", 1)[1].strip()

    return content

def generate_podcast(text: str, output_path: str, lang: str = "en") -> None:
    """
    Converts text to speech and saves as an MP3 file.
    """
    tts = gTTS(text=text, lang=lang)
    tts.save(output_path)
    print(f"🎧 Podcast saved at: {output_path}")

def run_pipeline(md_file_path: str) -> str:
    """
    Full pipeline: read Markdown → convert to audio → return path to .mp3
    """
    script_text = read_markdown(md_file_path)
    audio_path = os.path.splitext(md_file_path)[0] + ".mp3"
    generate_podcast(script_text, audio_path)
    return audio_path

# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    script_dir = os.path.dirname(__file__)
    md_file_path = os.path.join(script_dir,'..', 'generator', "motivational_script.md")

    mp3_path = run_pipeline(md_file_path)
    print(f"✅ Pipeline complete! Podcast ready at: {mp3_path}")
