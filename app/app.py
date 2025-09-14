
import os
import sys
import json
import streamlit as st

# -----------------------------
# Add project root to sys.path
# -----------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

# -----------------------------
# Import functions
# -----------------------------
from src.extractions.fitness_extractor import extract_fitness_profile
from src.nutritions_model.predict_meals import MealPredictor
from src.generator.planner_pipeline import generate_weekly_markdown
from src.generator.podcast_script import generate_motivational_script
from src.audio.podcast_pipeline_murf import run_pipeline_murf
from src.audio.podcast_pipeline import run_pipeline


# -----------------------------
# Paths
# -----------------------------
BASE_DIR = os.path.dirname(__file__)
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

WEEKLY_MD = os.path.join(OUTPUTS_DIR, "weekly_plan.md")
MOTIVATIONAL_MD = os.path.join(OUTPUTS_DIR, "motivational_script.md")
PODCAST_MP3 = os.path.join(OUTPUTS_DIR, "podcast.mp3")
USER_JSON = os.path.join(DATA_DIR, "user_data.json")
MEAL_JSON = os.path.join(DATA_DIR, "meal_plan.json")

# Ensure outputs folder exists
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🏋️‍♂️ Full Fitness Plan Generator with Podcast")

# Step 0: Ask user for paragraph input
user_paragraph = st.text_area(
    "Write a paragraph about yourself (fitness goals, habits, preferences, etc.):",
    height=200
)

if st.button("Generate Full Plan"):
    if not user_paragraph.strip():
        st.error("Please write something about yourself first!")
    else:
        try:
            # --- Step 1: Extract Fitness Profile ---
            extract_fitness_profile(user_paragraph, output_path=USER_JSON)
            st.success("✅ Fitness profile generated!")
            
            with open(USER_JSON, "r", encoding="utf-8") as f:
                user_data = json.load(f)
            # st.json(user_data)

                    # --- Step 2: Generate Meal Plan ---
            predictor = MealPredictor(model_dir=os.path.join(PROJECT_ROOT, "src", "nutritions_model"))

            meal_plan = predictor.predict_from_json(user_data, output_file=MEAL_JSON)
            st.success("✅ Meal plan generated!")

            # if meal_plan:
            #     st.json(meal_plan)



            with open(MEAL_JSON, "r", encoding="utf-8") as f:
                meal_data = json.load(f)
            # st.json(meal_data)

            # --- Step 3: Generate Weekly Plan ---
            generate_weekly_markdown(user_input=user_data[0])
            st.success("✅ Weekly plan generated!")

            if os.path.exists(WEEKLY_MD):
                with open(WEEKLY_MD, "r", encoding="utf-8") as f:
                    weekly_content = f.read()
                st.subheader("📋 Weekly Plan")
                st.markdown(weekly_content)
                st.download_button("⬇️ Download Weekly Plan (.md)", weekly_content, file_name="weekly_plan.md")


            # --- Step 4: Generate Motivational Script ---
            generate_motivational_script(md_file_path=WEEKLY_MD)
            st.success("✅ Motivational script generated!")

            if os.path.exists(MOTIVATIONAL_MD):
                with open(MOTIVATIONAL_MD, "r", encoding="utf-8") as f:
                    script_content = f.read()
                st.subheader("💬 Motivational Script")
                # st.text_area("Script", script_content, height=200)
                st.download_button("⬇️ Download Motivational Script (.md)", script_content, file_name="motivational_script.md")

            # --- Step 5: Generate Podcast Audio ---
            run_pipeline_murf(md_file_path=MOTIVATIONAL_MD, audio_output_path=PODCAST_MP3)
            st.success("✅ Podcast audio generated!")

            if os.path.exists(PODCAST_MP3):
                st.subheader("🎧 Podcast")
                st.audio(PODCAST_MP3)
                with open(PODCAST_MP3, "rb") as f:
                    st.download_button("⬇️ Download Podcast (.mp3)", f, file_name="podcast.mp3")

        except Exception as e:
            st.error(f"Error: {e}")
