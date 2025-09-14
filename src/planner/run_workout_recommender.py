"""Small runner for WorkoutRecommendationModel

This script trains the model on synthetic data, saves it to disk, and demonstrates a sample prediction.
"""
from workout_recommender import WorkoutRecommendationModel
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "workout_model.pkl")


def main():
    model = WorkoutRecommendationModel()
    print("Generating synthetic data...")
    data = model.create_synthetic_data(n_samples=2000)
    print(f"Training on {len(data)} samples")
    results = model.train_model(data)
    print("Training complete, saving model as .pkl...")
    model.save_model(MODEL_PATH)
    print(f"Saved model to: {MODEL_PATH}")

    # sample prediction
    user_input = {
        "gender": "female",
        "age": 28,
        "height": 165,
        "weight": 60,
        "fitness_level": "beginner",
        "activity_level": "lightly_active",
        "schedule": "morning weekdays",
        "nutrition": "balanced"
    }

    pred = model.predict_workout_plan(user_input)
    print("Sample prediction:")
    print(pred)


if __name__ == '__main__':
    main()
