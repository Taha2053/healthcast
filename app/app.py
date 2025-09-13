import os
import streamlit as st
import json
import sys

# Add project root to sys.path so Python can find src
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

# Import pipeline functions
from src.generator.planner_pipeline import generate_weekly_markdown
from src.generator.podcast_script import generate_motivational_script
from src.audio.podcast_pipeline import run_pipeline

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = os.path.dirname(__file__)
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

WEEKLY_MD = os.path.join(OUTPUTS_DIR, "weekly_plan.md")
MOTIVATIONAL_MD = os.path.join(OUTPUTS_DIR, "motivational_script.md")
PODCAST_MP3 = os.path.join(OUTPUTS_DIR, "podcast.mp3")

# Ensure outputs dir exists
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🏋️‍♂️ Fitness Plan Generator with Podcast")

uploaded_file = st.file_uploader("Upload your plan JSON", type="json")

if uploaded_file:
    user_data = json.load(uploaded_file)
    st.success("JSON uploaded successfully!")

    # --- Step 1: Weekly Plan ---
    try:
        generate_weekly_markdown(user_input=user_data[0])  
        st.success("✅ Weekly plan generated!")

        if os.path.exists(WEEKLY_MD):
            with open(WEEKLY_MD, "r", encoding="utf-8") as f:
                weekly_content = f.read()
            st.subheader("📋 Weekly Plan")
            st.markdown(weekly_content)
            st.download_button("⬇️ Download Weekly Plan (.md)", weekly_content, file_name="weekly_plan.md")
    except Exception as e:
        st.error(f"Error in Weekly Plan: {e}")

    # --- Step 2: Motivational Script ---
    try:
        generate_motivational_script(md_file_path=WEEKLY_MD)
        st.success("✅ Motivational script generated!")

        if os.path.exists(MOTIVATIONAL_MD):
            with open(MOTIVATIONAL_MD, "r", encoding="utf-8") as f:
                script_content = f.read()
            st.subheader("💬 Motivational Script")
            st.text_area("Script", script_content, height=200)
            st.download_button("⬇️ Download Motivational Script (.md)", script_content, file_name="motivational_script.md")
    except Exception as e:
        st.error(f"Error in Motivational Script: {e}")

    # --- Step 3: Podcast Audio ---
    try:
        run_pipeline(md_file_path=MOTIVATIONAL_MD, audio_output_path=PODCAST_MP3)
        st.success("✅ Podcast audio generated!")

        if os.path.exists(PODCAST_MP3):
            st.subheader("🎧 Podcast")
            st.audio(PODCAST_MP3)
            with open(PODCAST_MP3, "rb") as f:
                st.download_button("⬇️ Download Podcast (.mp3)", f, file_name="podcast.mp3")
    except Exception as e:
        st.error(f"Error in Podcast: {e}")
