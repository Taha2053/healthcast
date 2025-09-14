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
