import os
import streamlit as st

# -----------------------------
# Paths to generated files
# -----------------------------
BASE_DIR = os.path.dirname(__file__)
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")  # or wherever your files are

WEEKLY_MD = os.path.join(BASE_DIR, "..", 'src',"generator", "weekly_plan.md")
MOTIVATIONAL_MD = os.path.join(BASE_DIR, "..",'src', "generator", "motivational_script.md")
PODCAST_MP3 = os.path.join(BASE_DIR, "..", 'src',"audio", "podcast.mp3")

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🏋️‍♂️ Fitness Plan Viewer with Podcast")

# Weekly plan
if os.path.exists(WEEKLY_MD):
    with open(WEEKLY_MD, "r", encoding="utf-8") as f:
        weekly_content = f.read()
    st.subheader("📋 Weekly Plan")
    st.markdown(weekly_content)
    st.download_button("⬇️ Download Weekly Plan (.md)", weekly_content, file_name="weekly_plan.md")
else:
    st.warning("Weekly plan not found. Run planner_pipeline.py first.")

# Motivational script
if os.path.exists(MOTIVATIONAL_MD):
    with open(MOTIVATIONAL_MD, "r", encoding="utf-8") as f:
        script_content = f.read()
    st.subheader("💬 Motivational Script")
    st.text_area("Script", script_content, height=200)
    st.download_button("⬇️ Download Motivational Script (.md)", script_content, file_name="motivational_script.md")
else:
    st.warning("Motivational script not found. Run podcast_script.py first.")

# Podcast audio
if os.path.exists(PODCAST_MP3):
    st.subheader("🎧 Podcast")
    st.audio(PODCAST_MP3)
    with open(PODCAST_MP3, "rb") as f:
        st.download_button("⬇️ Download Podcast (.mp3)", f, file_name="podcast.mp3")
else:
    st.warning("Podcast not found. Run podcast_pipeline.py first.")
