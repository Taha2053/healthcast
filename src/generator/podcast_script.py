import os
import google.generativeai as genai
from dotenv import load_dotenv

# -----------------------------
# Load Gemini API key from .env
# -----------------------------
load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))


def generate_motivational_script(md_file_path=None) -> str:
    """
    Reads a Markdown file with user summary, workout plan, and nutrition plan,
    then generates a short, motivational fitness script using Gemini API.
    If md_file_path is None, it defaults to app/outputs/weekly_plan.md.
    """
    # Default outputs folder
    script_dir = os.path.dirname(__file__)
    outputs_dir = os.path.join(script_dir, "..",'..','app', "outputs")
    os.makedirs(outputs_dir, exist_ok=True)

    if md_file_path is None:
        md_file_path = os.path.join(outputs_dir, "weekly_plan.md")

    # Read the Markdown content
    with open(md_file_path, "r", encoding="utf-8") as f:
        markdown_content = f.read()

    # Prepare prompt for Gemini
    prompt = f"""
You are a friendly AI fitness coach. Read the following user info and weekly plan.
Write a short, motivational podcast-style script telling them to follow this plan.
Keep it positive, energetic, and under 2 minutes when read aloud.

User plan:

{markdown_content}
"""

    # Call Gemini API
    model = genai.GenerativeModel("gemini-2.5-pro")
    response = model.generate_content(prompt)

    motivational_script = response.text

    # Save the script to a Markdown file
    output_file = os.path.join(outputs_dir, "motivational_script.md")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Motivational Script\n\n")
        f.write(motivational_script + "\n")

    print(f"Motivational script saved at {output_file}")
    return motivational_script


# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    script_text = generate_motivational_script()
    print("Motivational Script:\n")
    print(script_text)
