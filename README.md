# Healthcast 🎧🏋️‍♀️🍎  

**Healthcast** is an AI-powered app that transforms a simple natural language prompt about your health, lifestyle, and goals into a **personalized fitness & nutrition plan**. It produces an engaging **podcast-style audio file** along with a **short markdown summary** that acts as a quick guide.  

---

## 🚀 Features  

- **Natural Language Input**: Users describe their height, weight, sports routine, and eating habits in plain English.  
- **Information Extraction**: Key details are extracted using regex, spaCy, and other NLP methods.  
- **Personalized Predictions**:  
  - 🏋️ Workout recommendations via **Random Forest**.  
  - 🍽️ Nutrition suggestions via **XGBoost**.  
- **LLM-based Generation**: Uses **Gemini** and **Murf** to transform raw predictions into a motivational podcast and concise plan.  
- **Engaging Output**:  
  - 🎙️ Downloadable podcast (`podcast.mp3`).  
  - 📑 Weekly plan summary in Markdown (`weekly_plan.md`).  
- **Web App Interface**: Built with **Streamlit** for simple interaction.  

---

## 🧩 Tech Stack  

- **Language**: Python 3  
- **NLP**: Regex, spaCy, custom extractors  
- **ML Models**: Random Forest (workouts), XGBoost (meals)  
- **Generative AI**: Gemini, Murf (script & audio generation)  
- **Web Framework**: Streamlit  
- **Audio**: Custom TTS pipeline for podcast output  

---

## 📂 Project Structure 
├── .env                           # Environment variables
├── .gitignore                     # Git ignore rules
├── requirements.txt               # Python dependencies
├── tree_structure.py              # Project structure generator
│
├── app/                           # Main application
│   ├── app.py                     # Flask/FastAPI main app
│   └── outputs/                   # Generated content
│       ├── motivational_script.md
│       ├── podcast.mp3
│       └── weekly_plan.md
│
├── data/                          # Data storage
│   ├── dataset_nutrition_random_forest/
│   ├── dataset_nutrition_xgboost/
│   ├── fitness_profiles.json      # User fitness data
│   ├── meal_plan.json             # Generated meal plans
│   ├── user_data.json             # User preferences
│   └── workout_plan.json          # Generated workout plans
│
├── src/                           # Source code
│   ├── audio/                     # Audio processing
│   │   └── podcast_pipeline.py   # Podcast generation pipeline
│   │
│   ├── extractions/               # Data extraction modules
│   │   ├── extraction.py          # General extraction utilities
│   │   ├── fitness_extractor.py   # Fitness data extraction
│   │   └── fitness_profiles.json  # Extracted fitness profiles
│   │
│   ├── generator/                 # Content generation
│   │   ├── planner_pipeline.py    # Planning pipeline
│   │   └── podcast_script.py      # Podcast script generator
│   │
│   ├── nutritions_model/          # Nutrition ML model
│   │   ├── encoders.pkl           # Label encoders
│   │   ├── food_encoders.pkl      # Food category encoders
│   │   ├── predict_meals.py       # Meal prediction logic
│   │   ├── scaler.pkl             # Feature scaler
│   │   ├── user.json              # User model data
│   │   └── xgb_meal_models.pkl    # XGBoost meal models
│   │
│   └── workout_model/             # Workout ML model (TBD)
│
├── notebooks/                     # Jupyter notebooks for analysis
├── tests/                         # Test files
│   └── test_pipeline.py           # Pipeline tests

---

## ⚙️ Installation  

1. Clone the repo:  
   ```bash
   git clone https://github.com/Taha2053/healthcast
   cd healthcast


Create a virtual environment and activate it:

python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows


Install dependencies:

pip install -r requirements.txt


Set up your .env file with the required API keys (Gemini, Murf, etc.).

▶️ Usage

Run the Streamlit app:

streamlit run app/app.py


Enter your health/lifestyle details in natural language.

The app generates:

🎙️ A motivational podcast audio (podcast.mp3).

📑 A weekly plan summary in Markdown (weekly_plan.md).

📊 Dataset & Models

Competition-provided fitness & nutrition datasets (not publicly available).

Custom-trained Random Forest (workout prediction).

Custom-trained XGBoost (meal prediction).

📝 The intermediate JSON files are used internally as model inputs to the LLM pipeline, not as end-user outputs.


👨‍💻 Contributors

Almouthana Taha Khalfallah
Salma Moueddeb
Eya Dhrif
Zaineb Darchem

📜 License

This project is licensed under the MIT License
.

✨ With Healthcast, fitness advice isn’t just data, it’s a podcast in your pocket!
