import os
import sys
import importlib.util
import json
import json

# -----------------------------
# Paths
# -----------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

DATA_DIR = os.path.join(PROJECT_ROOT, "data")
# Use the app/outputs folder so other modules that default to app/outputs can find files
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "app", "outputs")

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


def generate_weekly_markdown_in_main(fitness_profile_path, meal_plan_path, workout_plan_path, output_md_path):
    """Simple in-place markdown generator to avoid importing planner_pipeline.py which reads files on import.

    Args:
        fitness_profile_path (str): path to fitness_profiles.json (list) or a single profile
        meal_plan_path (str): path to meal_plan.json
        workout_plan_path (str): path to workout_plan.json
        output_md_path (str): path to write the markdown file
    """
    def safe_load(p):
        if not os.path.exists(p):
            return None
        with open(p, 'r', encoding='utf-8') as f:
            return json.load(f)

    fitness_profiles = safe_load(fitness_profile_path) or []
    meal_plan = safe_load(meal_plan_path) or {}
    workout_plan = safe_load(workout_plan_path) or {}

    # Choose first profile if list
    if isinstance(fitness_profiles, list):
        profile = fitness_profiles[0] if fitness_profiles else {}
    else:
        profile = fitness_profiles

    # Build markdown
    lines = []
    lines.append("# Your Weekly Health and Fitness Plan\n")
    lines.append("## Your Profile\n")
    lines.append(f"- Fitness Level: {profile.get('fitness_level', 'N/A')}")
    goals = profile.get('goals') or []
    if isinstance(goals, list):
        lines.append(f"- Goals: {', '.join(goals) if goals else 'N/A'}")
    else:
        lines.append(f"- Goals: {goals}")
    eq = profile.get('equipment_available') or []
    lines.append(f"- Available Equipment: {', '.join(eq) if eq else 'None'}\n")

    # Nutrition
    lines.append("## Weekly Meal Plan\n")
    if isinstance(meal_plan, dict):
        for item in meal_plan.get('meal_plan', []) if 'meal_plan' in meal_plan else meal_plan.items():
            # if meal_plan is dict with 'meal_plan' key
            if isinstance(item, dict) and 'meal' in item:
                day_label = item.get('meal')
                lines.append(f"### {day_label.capitalize()}\n")
                for food in item.get('foods', []):
                    lines.append(f"- {food.get('food', '')} ({food.get('amount','')})")
                if item.get('alternatives'):
                    lines.append('\n**Alternatives:**')
                    for alt in item['alternatives']:
                        lines.append(f"- {alt.get('dish')}: " + ", ".join([f"{f.get('food')} ({f.get('amount')})" for f in alt.get('foods', [])]))
                lines.append("")
            elif isinstance(item, tuple):
                # If iterating meal_plan.items()
                day, meals = item
                lines.append(f"### {day}\n")
                if isinstance(meals, dict):
                    for meal_type, meal_details in meals.items():
                        lines.append(f"#### {meal_type.capitalize()}")
                        if isinstance(meal_details, str):
                            lines.append(f"- {meal_details}")
                        elif isinstance(meal_details, dict):
                            for k, v in meal_details.items():
                                lines.append(f"- {k}: {v}")
                        lines.append("")

    # Workouts
    lines.append("## Weekly Workout Plan\n")
    if isinstance(workout_plan, dict):
        # workout_plan may be a mapping day -> list
        for k, v in workout_plan.items():
            lines.append(f"### {k.capitalize()}\n")
            if isinstance(v, list):
                for w in v:
                    if isinstance(w, dict):
                        lines.append(f"- {w.get('exercise','N/A')}")
                        lines.append(f"  - Sets: {w.get('sets','N/A')}")
                        lines.append(f"  - Reps: {w.get('reps','N/A')}")
                        if 'notes' in w:
                            lines.append(f"  - Notes: {w['notes']}")
                    else:
                        lines.append(f"- {w}")
            elif isinstance(v, str):
                lines.append(f"- {v}")
            lines.append("")

    os.makedirs(os.path.dirname(output_md_path), exist_ok=True)
    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"Weekly plan saved successfully at {output_md_path}")
    return output_md_path


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
    # Read the fitness profile JSON and pass a dict (not the filename string)
    if not os.path.exists(fitness_profile_path):
        raise FileNotFoundError(f"Expected fitness profile at {fitness_profile_path}")
    with open(fitness_profile_path, 'r', encoding='utf-8') as f:
        fitness_profiles = json.load(f)

    # If extractor appended profiles as a list, use the most recent entry
    if isinstance(fitness_profiles, list) and len(fitness_profiles) > 0:
        user_for_meals = fitness_profiles[-1]
    else:
        user_for_meals = fitness_profiles

    # Normalize user_for_meals fields so MealPredictor receives acceptable dtypes
    def normalize_user_for_meals(u: dict) -> dict:
        out = {}
        for k, v in (u or {}).items():
            # Flatten lists to comma-separated strings
            if isinstance(v, list):
                out[k] = ','.join(map(str, v)) if v else ''
            # Convert dicts to JSON string
            elif isinstance(v, dict):
                out[k] = json.dumps(v)
            else:
                out[k] = v

        # Ensure numerical fields exist
        try:
            if out.get('weight') and isinstance(out.get('weight'), str) and 'lb' in out.get('weight'):
                # crude conversion if weight was stored as string with pounds
                w = ''.join(ch for ch in out['weight'] if (ch.isdigit() or ch == '.'))
                out['weight'] = float(w) * 0.453592 if w else None
        except Exception:
            pass

        # Ensure BMI is numeric if present
        if out.get('bmi') is None and out.get('weight') and out.get('height'):
            try:
                h = float(out.get('height'))
                w = float(out.get('weight'))
                out['bmi'] = round(w / ((h / 100.0) ** 2), 1)
            except Exception:
                out['bmi'] = None

        return out

    user_for_meals = normalize_user_for_meals(user_for_meals)

    try:
        result = meal_predictor.predict_from_json(user_for_meals, output_file=meal_plan_path)
        if result is None:
            raise ValueError("Meal predictor returned None")
    except Exception as e:
        print(f"❌ Meal prediction failed: {e}")
        # Fallback simple meal plan so pipeline can continue
        fallback = {
            "meal_plan": [
                {"meal": "breakfast", "foods": [{"food": "Oatmeal", "amount": "50g"}]},
                {"meal": "lunch", "foods": [{"food": "Chicken Salad", "amount": "1 bowl"}]},
                {"meal": "dinner", "foods": [{"food": "Grilled Fish", "amount": "150g"}]} 
            ]
        }
        with open(meal_plan_path, 'w', encoding='utf-8') as f:
            json.dump(fallback, f, indent=2)
        print(f"Fallback meal plan written to {meal_plan_path}")

    # 3️⃣ Generate weekly markdown plan (implemented here to avoid importing broken planner module)
    md_plan_path = os.path.join(OUTPUTS_DIR, "weekly_plan.md")
    print("Generating weekly markdown plan...")
    generate_weekly_markdown_in_main(fitness_profile_path, meal_plan_path, WORKOUT_PLAN_PATH, md_plan_path)

    # 4️⃣ Generate motivational script
    podcast_script_path = os.path.join(PROJECT_ROOT, "src/generator/podcast_script.py")
    generate_motivational_script = dynamic_import(podcast_script_path, "generate_motivational_script")
    # The podcast script writes to app/outputs/motivational_script.md by default
    md_podcast_path = os.path.join(PROJECT_ROOT, "app", "outputs", "motivational_script.md")
    print("Generating motivational script...")
    # the function writes the output into app/outputs by default
    generate_motivational_script(md_file_path=md_plan_path)

    # 5️⃣ Generate podcast audio (Murf)
    podcast_pipeline_path = os.path.join(PROJECT_ROOT, "src/audio/podcast_pipeline_murf.py")
    run_pipeline_murf = dynamic_import(podcast_pipeline_path, "run_pipeline_murf")
    podcast_output_path = os.path.join(OUTPUTS_DIR, "podcast.mp3")
    print("Generating podcast audio...")
    run_pipeline_murf(md_file_path=md_podcast_path, audio_output_path=podcast_output_path)

    print("✅ Pipeline completed successfully!")


# -----------------------------
# Run example
# -----------------------------
if __name__ == "__main__":
    user_input_text = input("Enter your fitness goals or weekly plan: ")
    run_full_pipeline(user_input_text)
