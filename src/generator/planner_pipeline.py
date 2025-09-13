import json
import os

# Paths
script_dir = os.path.dirname(__file__)
json_path = os.path.join(script_dir, "..", "..", "data", "user_data.json")
output_dir = os.path.join(script_dir, "..",'..','app', "outputs")
os.makedirs(output_dir, exist_ok=True)  # ensure output folder exists

# Load user data from JSON
with open(json_path, "r") as f:
    user_data = json.load(f)


def generate_user_summary(user):
    """Create a short message summarizing the user's info."""
    summary = (
        f"Hello {user['gender']} aged {user['age']}!\n\n"
        f"Your goal is **{user['goal']}**, and your schedule is **{user['schedule']}**.\n"
        f"Based on your nutrition habits ({user['nutrition']}), here is your personalized plan.\n"
        "Follow this plan consistently for the best results!"
    )
    return summary


def generate_workout_markdown(user):
    """Generate a Markdown table for the workout plan."""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    md = "| Day | Workout |\n|---|---|\n"
    for i, day in enumerate(days):
        workout = user["workouts"][i % len(user["workouts"])]
        md += f"| {day} | {workout} |\n"
    return md


def generate_nutrition_markdown(user):
    """Generate a Markdown table for the nutrition plan."""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    md = "| Day | Meals |\n|---|---|\n"
    for i, day in enumerate(days):
        meal = user["meals"][i % len(user["meals"])]
        md += f"| {day} | {meal} |\n"
    return md


def generate_weekly_markdown(user_input=None):
    """
    Generate weekly plan Markdown.
    - If `user_input` is provided, use it.
    - Otherwise, use the first user from user_data.json.
    """
    user = user_input if user_input else user_data[0]

    summary_text = generate_user_summary(user)
    workout_md = generate_workout_markdown(user)
    nutrition_md = generate_nutrition_markdown(user)

    output_file = os.path.join(output_dir, "weekly_plan.md")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(summary_text + "\n\n")
        f.write("### Workout Plan\n\n")
        f.write(workout_md + "\n\n")
        f.write("### Nutrition Plan\n\n")
        f.write(nutrition_md + "\n")

    print(f"Weekly plan saved successfully at {output_file}")
    return output_file


# Example usage
if __name__ == "__main__":
    generate_weekly_markdown()
