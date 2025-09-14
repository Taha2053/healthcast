    import os
    import sys
    import json
    import logging
    from pathlib import Path

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    # Add project root to sys.path
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.append(PROJECT_ROOT)

    # Import required modules
    from src.extractions.fitness_extractor import extract_fitness_profile
    from src.nutritions_model.predict_meals import MealPredictor
    from src.generator.planner_pipeline import generate_weekly_markdown
    from src.generator.podcast_script import generate_motivational_script
    from src.audio.podcast_pipeline_murf import run_pipeline_murf

    # Define paths
    DATA_DIR = os.path.join(PROJECT_ROOT, "data")
    OUTPUT_DIR = os.path.join(PROJECT_ROOT, "app", "outputs")

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    def run_healthcast_pipeline():
        """
        Automates the entire healthcast pipeline from fitness extraction to podcast generation.
        """
        try:
            # 1. Extract fitness profile
            logger.info("Extracting fitness profile...")
            fitness_profile_path = os.path.join(DATA_DIR, "user_data.json")
            extract_fitness_profile()
            
            # 2. Generate meal plan
            logger.info("Generating meal plan...")
            meal_predictor = MealPredictor()
            with open(fitness_profile_path, 'r') as f:
                user_data = json.load(f)
                meal_plan = meal_predictor.predict_meals(user_data)
            
            meal_plan_path = os.path.join(DATA_DIR, "meal_plan.json")

            plan_output_path = os.path.join(OUTPUT_DIR, "comprehensive_plan.md")

            generate_weekly_markdown(user_input=fitness_profile)


            # 3. Generate workout and nutrition plan markdown
            logger.info("Generating comprehensive plan...")
            workout_plan_path = os.path.join(DATA_DIR, "workout_plan.json")
            plan_output_path = os.path.join(OUTPUT_DIR, "comprehensive_plan.md")
            generate_weekly_markdown(fitness_profile_path, meal_plan_path, workout_plan_path, plan_output_path)
            
            # 4. Generate motivational script
            logger.info("Generating motivational script...")
            motivational_script_path = os.path.join(OUTPUT_DIR, "motivational_script.md")
            generate_motivational_script(plan_output_path, motivational_script_path)
            
            # 5. Generate podcast audio
            logger.info("Generating podcast audio...")
            podcast_output_path = os.path.join(OUTPUT_DIR, "podcast.mp3")
            run_pipeline_murf(motivational_script_path, podcast_output_path)
            
            logger.info("Pipeline completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            raise

    if __name__ == "__main__":
        try:
            run_healthcast_pipeline()
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}")
            sys.exit(1)