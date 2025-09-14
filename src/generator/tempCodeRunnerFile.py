import json
import os
import sys

# -----------------------------
# Handle input arguments
# -----------------------------
# Optional: allow CLI args for input JSON and output folder
if len(sys.argv) >= 3:
    input_json = sys.argv[1]
    output_dir = sys.argv[2]
else:
    # Default paths
    script_dir = os.path.dirname(__file__)
    input_json = os.path.join(script_dir, "..", "..", "data", "user_data.json")
    meal_plan_json= os.path.join(script_dir, "..", "..", "data", "meal_plan.json")
    fitness_profile_json= os.path.join(script_dir, "..", "..", "data", "fitness_profiles.json")
    workout_plan_json= os.path.join(script_dir, "..", "..", "data", "workout_plan.json")
    with open(fitness_profile_json, "r", encoding="utf-8") as f:
        fitness_profiles = json.load(f)   
    with open(meal_plan_json, "r", encoding="utf-8") as f:
        meal_plans = json.load(f)       
    output_dir = os.path.join(script_dir, "..", "..", "app", "outputs")
    with open(workout_plan_json, "r", encoding="utf-8") as f:
        workout_plans = json.load(f)

os.makedirs(output_dir, exist_ok=True)

# Load user data
with open(input_json, "r", encoding="utf-8") as f:
    user_data = json.load(f)

######USER SUMMARY

def generate_user_summary(user):
    """Create a short message summarizing the user's info."""

    # Safely handle None values by converting them to empty lists
    goals = user.get("goals") or []
    if not isinstance(goals, list):
        goals = [goals]

    schedule = user.get("schedule_preferences") or []
    if not isinstance(schedule, list):
        schedule = [schedule]

    nutrition = user.get("nutrition_preferences") or []
    if not isinstance(nutrition, list):
        nutrition = [nutrition]

    summary = (
        f"Hello {user.get('gender', 'User')} aged {user.get('age', 'unknown')}!\n\n"
        f"Your goal(s): **{', '.join(goals) or 'no specific goals'}**, "
        f"and your schedule preference: **{', '.join(schedule) or 'no schedule preference'}**.\n"
        f"Based on your nutrition habits ({', '.join(nutrition) or 'no specific nutrition preferences'}), "
        "here is your personalized plan.\n"
        "Follow this plan consistently for the best results!"
    )
    return summary





def generate_workout_markdown(user):
    """Generate a Markdown table for the 7-day workout plan."""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    workouts = user.get("workouts", [])
    if not workouts:
        workouts = ["Rest"] * 7 

    md = "| Day | Workout |\n|---|---|\n"
    for i, day in enumerate(days):
        md += f"| {day} | {workouts[i % len(workouts)]} |\n"
    return md



def generate_nutrition_markdown(user):
    """Generate a Markdown table for the nutrition plan from the JSON meal_plan."""
    md = ""
    for meal in user["meal_plan"]:
        md += f"### {meal['meal'].capitalize()}\n\n"
        md += "**Recommended:**\n"
        for food in meal["foods"]:
            md += f"- {food['food']} ({food['amount']})\n"
        if meal.get("alternatives"):
            md += "\n**Alternatives:**\n"
            for alt in meal["alternatives"]:
                md += f"- {alt['dish']}: "
                md += ", ".join([f"{f['food']} ({f['amount']})" for f in alt["foods"]])
                md += "\n"
        md += "\n"
    return md





# def generate_weekly_markdown(user_input=None):
#     """
#     Generate weekly plan Markdown.
#     - If `user_input` is provided, use it.
#     - Otherwise, use the first user from user_data.json.
#     """
#     user = user_input if user_input else user_data[0]

#     summary_text = generate_user_summary(user)
#     workout_md = generate_workout_markdown(user)
#     nutrition_md = generate_nutrition_markdown(user)

#     output_file = os.path.join(output_dir, "weekly_plan.md")

#     with open(output_file, "w", encoding="utf-8") as f:
#         f.write(summary_text + "\n\n")
#         f.write("### Workout Plan\n\n")
#         f.write(workout_md + "\n\n")
#         f.write("### Nutrition Plan\n\n")
#         f.write(nutrition_md + "\n")

#     print(f"Weekly plan saved successfully at {output_file}")
#     return output_file



# def generate_weekly_markdown(user_input=None):
#     """
#     Generate weekly plan Markdown.
#     - If `user_input` is provided, use it.
#     - Otherwise, use user_data directly (assumes it's a dict)
#     """
#     meal_plan = meal_plan_json if user_input else user_data  # <-- no [0] indexing
#     profile = fitness_profile_json if user_input else user_data 
#     summary_text = generate_user_summary(profile)
#     # workout_md = generate_workout_markdown(user)
#     nutrition_md = generate_nutrition_markdown(meal_plan)

#     output_file = os.path.join(output_dir, "weekly_plan.md")

#     with open(output_file, "w", encoding="utf-8") as f:
#         f.write(summary_text + "\n\n")
#         # f.write("### Workout Plan\n\n")
#         # f.write(workout_md + "\n\n")
#         f.write("### Nutrition Plan\n\n")
#         f.write(nutrition_md + "\n")

#     print(f"Weekly plan saved successfully at {output_file}")
#     return output_file


# # -----------------------------
# # CLI execution
# # -----------------------------
# if __name__ == "__main__":
#     generate_weekly_markdown()



def generate_weekly_markdown(user_input=None):
    """
    Generate weekly plan Markdown.
    - If `user_input` is provided, use it.
    - Otherwise, use the first user from fitness_profiles.json.
    """
    profile = user_input if user_input else fitness_profiles[0]
    meal_plan = meal_plans  # use loaded meal_plan data
    workout_plan= workout_plans

    summary_text = generate_user_summary(profile)
    nutrition_md = generate_nutrition_markdown(meal_plan)
    workout_md = generate_workout_markdown(workout_plan)

    output_file = os.path.join(output_dir, "weekly_plan.md")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(summary_text + "\n\n")
        f.write("### Suggested Workout Plan\n\n")
        f.write(workout_md + "\n\n")    
        f.write("### Suggested Nutrition Plan\n\n")
        f.write(nutrition_md + "\n")

    print(f"Weekly plan saved successfully at {output_file}")
    return output_file

# -----------------------------
# CLI execution
# -----------------------------
if __name__ == "__main__":
    generate_weekly_markdown()