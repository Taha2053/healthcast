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


def run_pipeline(md_file_path=None, audio_output_path=None) -> str:
    """
    Full pipeline: read Markdown → convert to audio → return path to .mp3
    If paths are None, defaults to app/outputs folder.
    """
    script_dir = os.path.dirname(__file__)
    outputs_dir = os.path.join(script_dir, "..",'..','app', "outputs")
    os.makedirs(outputs_dir, exist_ok=True)

    if md_file_path is None:
        md_file_path = os.path.join(outputs_dir, "motivational_script.md")
    if audio_output_path is None:
        audio_output_path = os.path.join(outputs_dir, "podcast.mp3")

    script_text = read_markdown(md_file_path)
    generate_podcast(script_text, audio_output_path)

    return audio_output_path


# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    mp3_path = run_pipeline()
    print(f"✅ Pipeline complete! Podcast ready at: {mp3_path}")
