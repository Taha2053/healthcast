import json
import os

script_dir = os.path.dirname(__file__)  # directory of this script
json_path = os.path.join(script_dir, "..", "..", "data", "user_data.json")  # adjust path to reach data/
with open(json_path, "r") as f:
    user_data = json.load(f)

def generate_user_summary(user):
    """
    Create a short message summarizing the user's info.
    """
    summary = (
        f"Hello {user['gender']} aged {user['age']}!\n\n"
        f"Your goal is **{user['goal']}**, and your schedule is **{user['schedule']}**.\n"
        f"Based on your nutrition habits ({user['nutrition']}), here is your personalized plan.\n"
        "Follow this plan consistently for the best results!"
    )
    return summary


def generate_workout_markdown(user):
    """
    Generate a Markdown table for the workout plan.
    """
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    md = "| Day | Workout |\n|---|---|\n"
    for i, day in enumerate(days):
        workout = user["workouts"][i % len(user["workouts"])]
        md += f"| {day} | {workout} |\n"
    return md


def generate_nutrition_markdown(user):
    """
    Generate a Markdown table for the nutrition plan.
    """
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    md = "| Day | Meals |\n|---|---|\n"
    for i, day in enumerate(days):
        # Rotate meals so each day has one main meal from the list
        meal = user["meals"][i % len(user["meals"])]
        md += f"| {day} | {meal} |\n"
    return md


# Example usage
user = user_data[0]  # first user from JSON
summary_text = generate_user_summary(user)
workout_md = generate_workout_markdown(user)
nutrition_md = generate_nutrition_markdown(user)

# Print everything
print(summary_text + "\n\n")
print("### Workout Plan\n")
print(workout_md + "\n")
print("### Nutrition Plan\n")
print(nutrition_md)


# # Output to a Markdown file
# output_file = os.path.join(os.path.dirname(__file__), "weekly_plan.md")

# with open(output_file, "w", encoding="utf-8") as f:
#     # Write summary
#     f.write(summary_text + "\n\n")
    
#     # Write workout plan
#     f.write("### Workout Plan\n\n")
#     f.write(workout_md + "\n\n")
    
#     # Write nutrition plan
#     f.write("### Nutrition Plan\n\n")
#     f.write(nutrition_md + "\n")

# print(f"Weekly plan saved successfully at {output_file}")



def generate_weekly_markdown(user):
    summary_text = generate_user_summary(user)
    workout_md = generate_workout_markdown(user)
    nutrition_md = generate_nutrition_markdown(user)

    output_file = os.path.join(os.path.dirname(__file__), "weekly_plan.md")

    with open(output_file, "w", encoding="utf-8") as f:
        # Write summary
        f.write(summary_text + "\n\n")
        
        # Write workout plan
        f.write("### Workout Plan\n\n")
        f.write(workout_md + "\n\n")
        
        # Write nutrition plan
        f.write("### Nutrition Plan\n\n")
        f.write(nutrition_md + "\n")

    print(f"Weekly plan saved successfully at {output_file}")
    return output_file
