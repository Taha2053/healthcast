import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.pipeline import Pipeline
import json
import warnings
warnings.filterwarnings('ignore')

class WorkoutRecommendationModel:
    def __init__(self):
        self.model = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.workout_plans = {
            'muscle_gain': ["Day 1: Push", "Day 2: Pull", "Day 3: Legs", "Day 4: Push", "Day 5: Pull", "Day 6: HIIT", "Day 7: Rest"],
            'weight_loss': ["Day 1: HIIT", "Day 2: Full Body", "Day 3: Cardio", "Day 4: Upper Body", "Day 5: Lower Body", "Day 6: Cardio", "Day 7: Rest"],
            'endurance': ["Day 1: Long Cardio", "Day 2: Circuit Training", "Day 3: Interval Training", "Day 4: Cross Training", "Day 5: Endurance Run", "Day 6: Recovery Cardio", "Day 7: Rest"],
            'cardio': ["Day 1: Running", "Day 2: Cycling", "Day 3: Swimming", "Day 4: HIIT", "Day 5: Dance Cardio", "Day 6: Walking", "Day 7: Rest"]
        }
    
    def create_synthetic_data(self, n_samples=1000):
        """Create synthetic training data based on the structure shown in your datasets"""
        np.random.seed(42)
        
        # Generate user data
        ages = np.random.randint(17, 70, n_samples)
        heights = np.random.normal(170, 15, n_samples)  # cm
        weights = np.random.normal(70, 20, n_samples)   # kg
        
        # Calculate BMI
        bmis = weights / (heights/100)**2
        
        # Generate categorical features
        genders = np.random.choice(['male', 'female', 'other'], n_samples, p=[0.5, 0.45, 0.05])
        fitness_levels = np.random.choice(['beginner', 'intermediate', 'advanced'], n_samples, p=[0.3, 0.5, 0.2])
        activity_levels = np.random.choice(['sedentary', 'lightly_active', 'very_active', 'extremely_active'], n_samples, p=[0.2, 0.3, 0.4, 0.1])
        
        # Generate schedule preferences
        schedules = np.random.choice([
            'morning weekdays', 'evening weekdays', '6pm weekdays + weekends', 
            'weekends only', 'flexible', 'morning + evening'
        ], n_samples)
        
        # Generate nutrition patterns
        nutrition_patterns = np.random.choice([
            'balanced', 'high protein, low carbs', 'low protein, high carbs', 
            'high fat, low carbs', 'vegetarian', 'vegan'
        ], n_samples)
        
        # Generate goals based on user characteristics
        goals = []
        for i in range(n_samples):
            bmi = bmis[i]
            age = ages[i]
            fitness_level = fitness_levels[i]
            
            if bmi > 25 and age > 30:
                goal = np.random.choice(['weight_loss', 'cardio'], p=[0.7, 0.3])
            elif bmi < 20 and age < 30:
                goal = np.random.choice(['muscle_gain', 'endurance'], p=[0.8, 0.2])
            elif fitness_level == 'advanced':
                goal = np.random.choice(['muscle_gain', 'endurance'], p=[0.6, 0.4])
            else:
                goal = np.random.choice(['muscle_gain', 'weight_loss', 'endurance', 'cardio'], p=[0.3, 0.3, 0.2, 0.2])
            
            goals.append(goal)
        
        # Create DataFrame
        data = pd.DataFrame({
            'age': ages,
            'height': heights,
            'weight': weights,
            'bmi': bmis,
            'gender': genders,
            'fitness_level': fitness_levels,
            'activity_level': activity_levels,
            'schedule': schedules,
            'nutrition': nutrition_patterns,
            'goal': goals
        })
        
        return data
    
    def preprocess_data(self, data):
        """Preprocess the data for training"""
        # Create a copy to avoid modifying original data
        processed_data = data.copy()

        # Fill missing numeric values with column median
        numeric_cols = ['age', 'height', 'weight', 'bmi']
        for col in numeric_cols:
            if col in processed_data.columns:
                median = processed_data[col].median()
                processed_data[col] = processed_data[col].fillna(median)

        # Encode categorical variables using LabelEncoder, but handle unseen categories at predict time
        categorical_columns = ['gender', 'fitness_level', 'activity_level', 'schedule', 'nutrition']

        for col in categorical_columns:
            if col in processed_data.columns:
                # Fill missing categorical with a placeholder
                processed_data[col] = processed_data[col].fillna('__missing__')

                if col not in self.label_encoders:
                    le = LabelEncoder()
                    processed_data[col] = le.fit_transform(processed_data[col])
                    # store classes_ so we can handle unseen categories later
                    self.label_encoders[col] = le
                else:
                    le = self.label_encoders[col]
                    # For unseen categories, map them to a reserved index (len(classes_)) and extend classes_
                    known_classes = set(le.classes_)
                    vals = processed_data[col].astype(str).tolist()
                    mapped = []
                    for v in vals:
                        if v in known_classes:
                            mapped.append(v)
                        else:
                            mapped.append('__unseen__')
                    # Temporarily fit transform by extending classes_ if needed
                    if '__unseen__' not in le.classes_:
                        le.classes_ = np.append(le.classes_, '__unseen__')
                    processed_data[col] = le.transform(mapped)

        # Encode target variable if present
        y = None
        if 'goal' in processed_data.columns:
            processed_data['goal'] = processed_data['goal'].fillna('__missing__')
            if 'goal' not in self.label_encoders:
                self.label_encoders['goal'] = LabelEncoder()
                y = self.label_encoders['goal'].fit_transform(processed_data['goal'])
            else:
                # handle unseen goal labels similarly
                le_goal = self.label_encoders['goal']
                vals = processed_data['goal'].astype(str).tolist()
                known = set(le_goal.classes_)
                mapped = [v if v in known else '__unseen__' for v in vals]
                if '__unseen__' not in le_goal.classes_:
                    le_goal.classes_ = np.append(le_goal.classes_, '__unseen__')
                y = le_goal.transform(mapped)

        # Select features
        feature_columns = [c for c in ['age', 'height', 'weight', 'bmi', 'gender', 'fitness_level',
                                       'activity_level', 'schedule', 'nutrition'] if c in processed_data.columns]
        X = processed_data[feature_columns]

        return X, y

    def save_model(self, path):
        """Save trained model, label encoders and scaler to disk using joblib"""
        try:
            import joblib
        except Exception:
            raise RuntimeError("joblib is required to save/load models. Install it in your environment.")

        payload = {
            'model': self.model,
            'label_encoders': self.label_encoders,
            'workout_plans': self.workout_plans
        }
        joblib.dump(payload, path)

    def load_model(self, path):
        try:
            import joblib
        except Exception:
            raise RuntimeError("joblib is required to save/load models. Install it in your environment.")

        payload = joblib.load(path)
        self.model = payload.get('model')
        self.label_encoders = payload.get('label_encoders', {})
        self.workout_plans = payload.get('workout_plans', self.workout_plans)

    def predict_proba(self, user_input):
        """Return probability distribution over goals for a single user input"""
        if self.model is None:
            raise ValueError("Model not trained yet!")

        user_df = pd.DataFrame([user_input])
        if 'bmi' not in user_df.columns and 'weight' in user_df.columns and 'height' in user_df.columns:
            user_df['bmi'] = user_df['weight'] / (user_df['height']/100)**2

        X_user, _ = self.preprocess_data(user_df)
        if hasattr(self.model, 'predict_proba'):
            probs = self.model.predict_proba(X_user)[0]
            classes = self.label_encoders['goal'].inverse_transform(np.arange(len(probs)))
            return dict(zip(classes, probs.tolist()))
        else:
            # fallback: return 1 for predicted class
            pred = self.model.predict(X_user)[0]
            cls = self.label_encoders['goal'].inverse_transform([pred])[0]
            return {cls: 1.0}
    
    def train_model(self, data):
        """Train the model with cross-validation to avoid overfitting"""
        print("Preprocessing data...")
        X, y = self.preprocess_data(data)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Create pipeline with scaling and random forest
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('classifier', RandomForestClassifier(random_state=42))
        ])
        
        # Hyperparameter tuning to avoid overfitting
        param_grid = {
            'classifier__n_estimators': [50, 100, 200],
            'classifier__max_depth': [3, 5, 7, None],
            'classifier__min_samples_split': [2, 5, 10],
            'classifier__min_samples_leaf': [1, 2, 4],
            'classifier__max_features': ['sqrt', 'log2']
        }
        
        print("Performing hyperparameter tuning...")
        grid_search = GridSearchCV(
            pipeline, 
            param_grid, 
            cv=5, 
            scoring='accuracy',
            n_jobs=-1,
            verbose=1
        )
        
        grid_search.fit(X_train, y_train)
        self.model = grid_search.best_estimator_
        
        print(f"Best parameters: {grid_search.best_params_}")
        
        # Cross-validation to check for overfitting
        cv_scores = cross_val_score(self.model, X_train, y_train, cv=5, scoring='accuracy')
        print(f"Cross-validation scores: {cv_scores}")
        print(f"Mean CV accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        # Test set evaluation
        y_pred = self.model.predict(X_test)
        test_accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\nTest Set Results:")
        print(f"Test accuracy: {test_accuracy:.4f}")
        print(f"\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=self.label_encoders['goal'].classes_))
        
        # Check for overfitting
        train_accuracy = self.model.score(X_train, y_train)
        print(f"\nOverfitting Analysis:")
        print(f"Training accuracy: {train_accuracy:.4f}")
        print(f"Test accuracy: {test_accuracy:.4f}")
        print(f"Difference: {train_accuracy - test_accuracy:.4f}")
        
        if train_accuracy - test_accuracy > 0.1:
            print("⚠️ Warning: Model might be overfitting!")
        else:
            print("✅ Model appears to be well-generalized.")
        
        return {
            'cv_accuracy': cv_scores.mean(),
            'test_accuracy': test_accuracy,
            'train_accuracy': train_accuracy,
            'overfitting_gap': train_accuracy - test_accuracy
        }
    
    def predict_workout_plan(self, user_input):
        """Predict workout plan for a new user"""
        if self.model is None:
            raise ValueError("Model not trained yet!")
        
        # Convert user input to DataFrame
        user_df = pd.DataFrame([user_input])
        
        # Calculate BMI if not provided
        if 'bmi' not in user_df.columns:
            user_df['bmi'] = user_df['weight'] / (user_df['height']/100)**2
        
        # Preprocess
        X_user, _ = self.preprocess_data(user_df)
        
        # Predict
        goal_encoded = self.model.predict(X_user)[0]
        goal = self.label_encoders['goal'].inverse_transform([goal_encoded])[0]
        
        # Get workout plan
        workout_plan = self.workout_plans.get(goal, self.workout_plans['muscle_gain'])
        
        # Create output JSON
        result = {
            "gender": user_input['gender'],
            "age": user_input['age'],
            "height": user_input['height'],
            "weight": user_input['weight'],
            "schedule": user_input['schedule'],
            "nutrition": user_input['nutrition'],
            "goal": goal,
            "workouts": workout_plan
        }
        
        return result

# Example usage
def main():
    # Initialize model
    model = WorkoutRecommendationModel()
    
    # Create synthetic training data
    print("Creating synthetic training data...")
    training_data = model.create_synthetic_data(n_samples=2000)
    print(f"Generated {len(training_data)} training samples")
    
    # Train model
    print("\nTraining model...")
    results = model.train_model(training_data)
    
    # Example prediction
    print("\n" + "="*50)
    print("EXAMPLE PREDICTION")
    print("="*50)
    
    user_input = {
        "gender": "male",
        "age": 22,
        "height": 175,
        "weight": 70,
        "fitness_level": "intermediate",
        "activity_level": "very_active",
        "schedule": "6pm weekdays + weekends",
        "nutrition": "low protein, high carbs"
    }
    
    prediction = model.predict_workout_plan(user_input)
    print("User Input:", json.dumps(user_input, indent=2))
    print("\nPredicted Workout Plan:")
    print(json.dumps(prediction, indent=2))
    
    return model, results

if __name__ == "__main__":
    model, results = main()