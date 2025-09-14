import pandas as pd
import json
import joblib
import numpy as np
import argparse
import sys
from pathlib import Path

class MealPredictor:
    def __init__(self, model_dir="./"):
        """
        Initialize the meal predictor by loading trained models and preprocessors
        
        Args:
            model_dir (str): Directory containing the saved model files
        """
        self.model_dir = Path(model_dir)
        self.models = None
        self.encoders = None
        self.scaler = None
        self.food_encoders = None
        self.categorical_cols = ["gender", "fitness_level", "activity_level", "goals"]
        
        # Food library with portions
        self.food_library = {
            "Oatmeal": [("Oatmeal", "50g"), ("Banana", "1 piece"), ("Milk", "200ml")],
            "Eggs": [("Eggs", "2 pieces"), ("Toast", "2 slices"), ("Orange Juice", "250ml")],
            "Smoothie": [("Smoothie", "300ml"), ("Granola", "30g")],
            "Chicken Salad": [("Chicken Breast", "120g"), ("Lettuce", "50g"), ("Olive Oil", "10ml")],
            "Rice & Beans": [("Rice", "100g"), ("Beans", "80g"), ("Avocado", "50g")],
            "Grilled Fish": [("Fish", "150g"), ("Quinoa", "100g"), ("Spinach", "60g")],
            "Pasta": [("Pasta", "120g"), ("Tomato Sauce", "80g"), ("Parmesan", "20g")],
            "Grilled Salmon": [("Salmon", "150g"), ("Asparagus", "80g"), ("Sweet Potato", "100g")],
            "Steak": [("Steak", "180g"), ("Mashed Potatoes", "100g"), ("Green Beans", "70g")],
            "Vegetable Soup": [("Soup", "300ml"), ("Bread", "1 slice")],
            "Chicken Wrap": [("Chicken", "100g"), ("Tortilla", "1 piece"), ("Lettuce", "40g")]
        }
        
        self.load_models()
    
    def load_models(self):
        """Load all trained models and preprocessors"""
        try:
            print("Loading trained models and preprocessors...")
            
            # Load models and preprocessors
            self.models = joblib.load(self.model_dir / "xgb_meal_models.pkl")
            self.encoders = joblib.load(self.model_dir / "encoders.pkl")
            self.scaler = joblib.load(self.model_dir / "scaler.pkl")
            self.food_encoders = joblib.load(self.model_dir / "food_encoders.pkl")
            
            print("✓ Models loaded successfully!")
            print(f"✓ Available meal models: {list(self.models.keys())}")
            
        except FileNotFoundError as e:
            print(f"❌ Error: Could not find model files in {self.model_dir}")
            print("Make sure you have run the training script first and have these files:")
            print("  - xgb_meal_models.pkl")
            print("  - encoders.pkl")
            print("  - scaler.pkl") 
            print("  - food_encoders.pkl")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            sys.exit(1)
    
    def expand_meal(self, pred):
        """Expand predicted dish into full meal with portions"""
        return [{"food": food, "amount": amount} 
                for food, amount in self.food_library.get(pred, [(pred, "1 serving")])]
    
    def get_prediction_probabilities(self, user_features, meal_type):
        """Get prediction probabilities for better insights"""
        model = self.models[meal_type]
        probabilities = model.predict_proba(user_features)[0]
        classes = self.food_encoders[f"{meal_type}_food"].classes_
        
        # Create probability dictionary
        prob_dict = dict(zip(classes, probabilities))
        # Sort by probability
        sorted_probs = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_probs
    
    def preprocess_user_data(self, user_data):
        """
        Preprocess user data using saved encoders and scaler
        
        Args:
            user_data (dict): User information dictionary
            
        Returns:
            pandas.DataFrame: Preprocessed features ready for prediction
        """
        # Convert to DataFrame
        user_df = pd.DataFrame([user_data])
        
        # Encode categorical variables with fallback to "unknown"
        for col in self.categorical_cols:
            if col in user_df.columns:
                user_df[col] = user_df[col].astype(str)
                # Handle unknown categories
                user_df[col] = user_df[col].apply(
                    lambda x: x if x in self.encoders[col].classes_ else "unknown"
                )
                user_df[col] = self.encoders[col].transform(user_df[col])
            else:
                print(f"⚠️  Warning: Column '{col}' not found in user data, using 'unknown'")
                user_df[col] = self.encoders[col].transform(["unknown"])
        
        # Scale numerical features
        numerical_cols = ["age", "weight", "height", "bmi"]
        if all(col in user_df.columns for col in numerical_cols):
            user_df[numerical_cols] = self.scaler.transform(user_df[numerical_cols])
        else:
            missing_cols = [col for col in numerical_cols if col not in user_df.columns]
            raise ValueError(f"Missing required numerical columns: {missing_cols}")
        
        # Remove user_id if present
        if "user_id" in user_df.columns:
            user_df = user_df.drop(columns=["user_id"])
        
        return user_df
    
    def predict_meals(self, user_data, show_alternatives=True, top_alternatives=3):
        """
        Generate meal plan for a user
        
        Args:
            user_data (dict): User information
            show_alternatives (bool): Whether to include alternative meal suggestions
            top_alternatives (int): Number of alternative suggestions to include
            
        Returns:
            dict: Generated meal plan with recommendations
        """
        try:
            # Preprocess user data
            X_user = self.preprocess_user_data(user_data)
            
            meal_plan = {"meal_plan": []}
            
            for meal_type in ['breakfast', 'lunch', 'dinner']:
                # Main prediction
                pred_encoded = self.models[meal_type].predict(X_user)[0]
                main_pred = self.food_encoders[f"{meal_type}_food"].inverse_transform([pred_encoded])[0]
                
                meal_info = {
                    "meal": meal_type,
                    "recommended": main_pred,
                    "foods": self.expand_meal(main_pred)
                }
                
                # Add alternatives if requested
                if show_alternatives:
                    probabilities = self.get_prediction_probabilities(X_user, meal_type)
                    alternatives = []
                    
                    # Get top alternatives (excluding the main prediction)
                    for food, prob in probabilities[1:top_alternatives+1]:
                        alternatives.append({
                            "dish": food,
                            "confidence": f"{prob:.2%}",
                            "foods": self.expand_meal(food)
                        })
                    
                    meal_info["alternatives"] = alternatives
                    meal_info["main_confidence"] = f"{probabilities[0][1]:.2%}"
                
                meal_plan["meal_plan"].append(meal_info)
            
            return meal_plan
            
        except Exception as e:
            print(f"❌ Error during prediction: {e}")
            return None
    
    def predict_from_json(self, json_input, output_file=None):
        """
        Generate meal plan from JSON input
        
        Args:
            json_input (str or dict): JSON string or dictionary with user data
            output_file (str): Optional output file path
            
        Returns:
            dict: Generated meal plan
        """
        # Parse JSON if string
        if isinstance(json_input, str):
            try:
                user_data = json.loads(json_input)
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing JSON: {e}")
                return None
        else:
            user_data = json_input
        
        # Generate meal plan
        meal_plan = self.predict_meals(user_data)
        
        if meal_plan is None:
            return None
        
        # Save to file if specified
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    json.dump(meal_plan, f, indent=2)
                print(f"✓ Meal plan saved to: {output_file}")
            except Exception as e:
                print(f"❌ Error saving to file: {e}")
        
        return meal_plan

def main():
    # Get the directory where this script is located
    script_dir = Path(__file__).parent

    # Input JSON file in '../../data/user.json'
    input_file = script_dir / ".." / ".." / "data" / "user.json"
    input_file = input_file.resolve()  # optional: get absolute path

    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        sys.exit(1)

    # Load user data
    try:
        with open(input_file, 'r') as f:
            user_data = json.load(f)
        print(f"✓ Loaded user data from: {input_file}")
    except Exception as e:
        print(f"❌ Error reading input file: {e}")
        sys.exit(1)

    # Output file in the same folder
    output_dir = script_dir / ".." / ".." / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "meal_plan.json"

    # Generate meal plan
    print(f"\nGenerating meal plan for user: {user_data.get('user_id', 'Unknown')}")
    predictor = MealPredictor(model_dir=script_dir)
    meal_plan = predictor.predict_meals(user_data, show_alternatives=True)

    if meal_plan:
        # Save to output file
        with open(output_file, 'w') as f:
            json.dump(meal_plan, f, indent=2)
        print(f"✓ Meal plan generated and saved to: {output_file}")
    else:
        print("❌ Failed to generate meal plan")
        sys.exit(1)

if __name__ == "__main__":
    main()