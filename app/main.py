import os
import sys
import importlib.util

# -----------------------------
# Paths
# -----------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

DATA_DIR = os.path.join(PROJECT_ROOT, "data")
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

WORKOUT_PLAN_PATH = os.path.join(DATA_DIR, "workout_plan.json")


# -----------------------------
# Helper: dynamic import
# -----------------------------
def dynamic_import(module_path, func_name):
    spec = importlib.util.spec_from_file_location("module.name", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, func_name)


# -----------------------------
# Main pipeline
# -----------------------------
def run_full_pipeline(user_input_text: str):
    # 1️⃣ Run fitness_extractor
    fitness_extractor_path = os.path.join(PROJECT_ROOT, "src/extractions/fitness_extractor.py")
    extract_fitness_profile = dynamic_import(fitness_extractor_path, "extract_fitness_profile")
    fitness_profile_path = os.path.join(DATA_DIR, "fitness_profile.json")
    print("Extracting fitness profile...")
    extract_fitness_profile(user_input_text, output_path=fitness_profile_path)

    # 2️⃣ Run MealPredictor from predict_meals.py
    predict_meals_path = os.path.join(PROJECT_ROOT, "src/nutritions_model/predict_meals.py")
    MealPredictor = dynamic_import(predict_meals_path, "MealPredictor")

    # Correct folder where your .pkl models live
    meal_models_dir = os.path.join(PROJECT_ROOT, "src", "nutritions_model")

    meal_plan_path = os.path.join(DATA_DIR, "meal_plan.json")
    print("Generating meal plan...")

    # Pass the correct model_dir
    meal_predictor = MealPredictor(model_dir=meal_models_dir)

    # Use predict_from_json to generate the meal plan JSON
    meal_predictor.predict_from_json(fitness_profile_path, output_file=meal_plan_path)

    # 3️⃣ Generate weekly markdown plan
    planner_pipeline_path = os.path.join(PROJECT_ROOT, "src/generator/planner_pipeline.py")
    generate_weekly_markdown = dynamic_import(planner_pipeline_path, "generate_weekly_markdown")
    md_plan_path = os.path.join(OUTPUTS_DIR, "weekly_plan.md")
    print("Generating weekly markdown plan...")
    generate_weekly_markdown(
        workout_path=WORKOUT_PLAN_PATH,
        fitness_path=fitness_profile_path,
        meals_path=meal_plan_path,
        output_md_path=md_plan_path
    )

    # 4️⃣ Generate motivational script
    podcast_script_path = os.path.join(PROJECT_ROOT, "src/generator/podcast_script.py")
    generate_motivational_script = dynamic_import(podcast_script_path, "generate_motivational_script")
    md_podcast_path = os.path.join(OUTPUTS_DIR, "motivational_script.md")
    print("Generating motivational script...")
    generate_motivational_script(md_file_path=md_plan_path, output_md_path=md_podcast_path)

    # 5️⃣ Generate podcast audio
    podcast_pipeline_path = os.path.join(PROJECT_ROOT, "src/audio/podcast_pipeline.py")
    run_pipeline = dynamic_import(podcast_pipeline_path, "run_pipeline")
    print("Generating podcast audio...")
    run_pipeline(md_podcast_path, output_dir=OUTPUTS_DIR)

    print("✅ Pipeline completed successfully!")


# -----------------------------
# Run example
# -----------------------------
if __name__ == "__main__":
    user_input_text = input("Enter your fitness goals or weekly plan: ")
    run_full_pipeline(user_input_text)
