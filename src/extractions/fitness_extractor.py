import re
import json
import logging
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import re
import json
import logging
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FitnessLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class ActivityLevel(Enum):
    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly active"
    MODERATELY_ACTIVE = "moderately active"
    VERY_ACTIVE = "very active"
    EXTRA_ACTIVE = "extra active"

class Gender(Enum):
    MALE = "male"
    FEMALE = "female"

class BMICategory(Enum):
    UNDERWEIGHT = "underweight"
    NORMAL = "normal"
    OVERWEIGHT = "overweight"
    OBESE = "obese"

@dataclass
class FitnessProfile:
    """Enhanced fitness profile with validation and computed properties."""
    age: Optional[int] = None
    weight: Optional[float] = None  # Always stored in kg
    height: Optional[float] = None  # Always stored in cm
    bmi: Optional[float] = None
    bmi_category: Optional[str] = None
    fitness_level: Optional[str] = None
    goals: Optional[str] = None  # comma-separated string
    gender: Optional[str] = None
    activity_level: Optional[str] = None
    nutrition_preferences: Optional[str] = None
    schedule_preferences: Optional[str] = None
    medical_conditions: List[str] = field(default_factory=list)
    equipment_available: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self._validate_fields()
        if self.weight and self.height and not self.bmi:
            self.bmi = self._calculate_bmi(self.weight, self.height)
            self.bmi_category = self._categorize_bmi(self.bmi)
    
    def _validate_fields(self):
        if self.age is not None and (self.age < 0 or self.age > 150):
            logger.warning(f"Unusual age value: {self.age}")
        if self.weight is not None and (self.weight < 20 or self.weight > 500):
            logger.warning(f"Unusual weight value: {self.weight}kg")
        if self.height is not None and (self.height < 50 or self.height > 300):
            logger.warning(f"Unusual height value: {self.height}cm")
    
    @staticmethod
    def _calculate_bmi(weight: float, height: float) -> float:
        height_m = height / 100.0
        return round(weight / (height_m ** 2), 1)
    
    @staticmethod
    def _categorize_bmi(bmi: float) -> str:
        if bmi < 18.5:
            return BMICategory.UNDERWEIGHT.value
        elif bmi < 25:
            return BMICategory.NORMAL.value
        elif bmi < 30:
            return BMICategory.OVERWEIGHT.value
        else:
            return BMICategory.OBESE.value
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        # Convert goals to list if present
        if result.get("goals"):
            result["goals"] = result["goals"].split(",")
        return {k: v for k, v in result.items() if v is not None and v != [] and v != ""}

# ------------------ Extractors ------------------

class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, text: str) -> Any:
        pass

class PatternExtractor(BaseExtractor):
    def __init__(self, patterns: Union[str, List[str]], flags: int = re.IGNORECASE):
        self.patterns = patterns if isinstance(patterns, list) else [patterns]
        self.flags = flags
    
    def extract(self, text: str) -> Optional[re.Match]:
        for pattern in self.patterns:
            match = re.search(pattern, text, self.flags)
            if match:
                return match
        return None

class AgeExtractor(PatternExtractor):
    def __init__(self):
        patterns = [
            r'(\d+)\s*(?:years?\s*old|yrs?\s*old|yo)',
            r'(?:age|aged?)[:\s]*(\d+)',
            r'\b(\d+)\s*(?:years?|yrs?)\b'
        ]
        super().__init__(patterns)
    
    def extract(self, text: str) -> Optional[int]:
        match = super().extract(text)
        if match:
            age = int(match.group(1))
            return age if 1 <= age <= 120 else None
        return None

class WeightExtractor(PatternExtractor):
    def __init__(self):
        patterns = [
            r'(?:weight|weigh)\s*(\d+(?:\.\d+)?)\s*(?:kg|kilograms?)',
            r'(?:weight|weigh)\s*(\d+(?:\.\d+)?)\s*(?:lbs?|pounds?)',
            r'\b(\d+(?:\.\d+)?)\s*(?:kg|kilograms?)\b',
            r'\b(\d+(?:\.\d+)?)\s*(?:lbs?|pounds?)\b'
        ]
        super().__init__(patterns)
    
    def extract(self, text: str) -> Optional[float]:
        match = super().extract(text)
        if match:
            weight = float(match.group(1))
            if re.search(r'lbs?|pounds?', match.group(0), re.IGNORECASE):
                weight *= 0.453592
            return round(weight, 1) if 20 <= weight <= 500 else None
        return None

class HeightExtractor(PatternExtractor):
    def __init__(self):
        patterns = [
            r"(\d+)'(\d+)\"",
            r'(\d+)\s*(?:feet|ft)\s*(\d+)\s*(?:inches?|in)',
            r'(\d+\.\d+)\s*(?:m|meters?)\b',
            r'\b(\d+)\s*(?:cm|centimeters?)\b',
            r'(?:height|tall)[:\s]*(\d+)\s*(?:cm|centimeters?)',
            r'(\d+)\s*(?:m|meters?)\s*(\d+)\s*(?:cm|centimeters?)'
        ]
        super().__init__(patterns)
    
    def extract(self, text: str) -> Optional[float]:
        match = super().extract(text)
        if match:
            groups = match.groups()
            if len(groups) == 1:
                if 'm' in match.group(0) and '.' in match.group(1):
                    return round(float(groups[0]) * 100, 1)
                else:
                    return float(groups[0])
            elif len(groups) == 2:
                if 'm' in match.group(0) and 'cm' in match.group(0):
                    return round(float(groups[0]) * 100 + float(groups[1]), 1)
                else:
                    return round((float(groups[0])*30.48) + (float(groups[1])*2.54), 2)
        return None

class EnumExtractor(PatternExtractor):
    def __init__(self, enum_class, additional_mappings=None):
        self.enum_class = enum_class
        self.mappings = additional_mappings or {}
        values = [e.value for e in enum_class] + list(self.mappings.keys())
        pattern = r'\b(' + '|'.join(re.escape(v) for v in values) + r')\b'
        super().__init__(pattern)
    
    def extract(self, text: str) -> Optional[str]:
        match = super().extract(text)
        if match:
            found_value = match.group(1).lower()
            for enum_val in self.enum_class:
                if enum_val.value == found_value:
                    return enum_val.value
            if found_value in self.mappings:
                return self.mappings[found_value]
        return None

class GoalsExtractor(PatternExtractor):
    def __init__(self):
        self.goal_mappings = {
            'weight loss': ['lose weight', 'weight loss', 'fat loss', 'slim down'],
            'muscle building': ['muscle building', 'build muscle', 'gain muscle', 'muscle gain', 'bulking'],
            'endurance': ['endurance', 'cardio', 'stamina', 'cardiovascular'],
            'flexibility': ['flexibility', 'stretching', 'mobility'],
            'general fitness': ['general fitness', 'overall fitness', 'get fit', 'fitness'],
            'strength': ['strength', 'get strong', 'get stronger', 'power']
        }
        all_terms = []
        for terms in self.goal_mappings.values():
            all_terms.extend(terms)
        pattern = r'\b(' + '|'.join(re.escape(t) for t in all_terms) + r')\b'
        super().__init__(pattern)
    
    def extract(self, text: str) -> Optional[str]:
        matches = re.findall(self.patterns[0], text, self.flags)
        found_goals = set()
        for match in matches:
            for goal, terms in self.goal_mappings.items():
                if match.lower() in terms:
                    found_goals.add(goal)
        return ','.join(sorted(found_goals)) if found_goals else None

# ------------------ Main Extractor ------------------

class FitnessProfileExtractor:
    def __init__(self):
        self.age_extractor = AgeExtractor()
        self.weight_extractor = WeightExtractor()
        self.height_extractor = HeightExtractor()
        self.goals_extractor = GoalsExtractor()
        gender_mappings = {'man': 'male', 'boy': 'male', 'woman': 'female', 'girl': 'female'}
        self.gender_extractor = EnumExtractor(Gender, gender_mappings)
        self.fitness_level_extractor = EnumExtractor(FitnessLevel)
        self.activity_level_extractor = EnumExtractor(ActivityLevel)
    
    def extract(self, text: str) -> FitnessProfile:
        try:
            profile = FitnessProfile(
                age=self.age_extractor.extract(text),
                weight=self.weight_extractor.extract(text),
                height=self.height_extractor.extract(text),
                fitness_level=self.fitness_level_extractor.extract(text),
                goals=self.goals_extractor.extract(text),
                gender=self.gender_extractor.extract(text),
                activity_level=self.activity_level_extractor.extract(text)
            )
            return profile
        except Exception as e:
            logger.error(f"Error extracting profile: {e}")
            return FitnessProfile()
    
    def extract_batch(self, texts: List[str]) -> List[FitnessProfile]:
        return [self.extract(text) for text in texts]

# ------------------ Main ------------------

def main():
    extractor = FitnessProfileExtractor()
    test_cases = [
        "Hi! I am a 22 year old female. My weight is 68 kg and my height is 175 cm. I am a beginner and very active. My goals are weight loss and muscle building.",
        "Male, 30 yrs old, weigh 180 pounds, 5'9 tall, intermediate fitness level, moderately active, goal: endurance and strength",
        "I'm a 40 years old woman, 60kg, 165cm, advanced level, lightly active, want flexibility and fat loss",
        "25yo man, 1.80m tall, 75kg, beginner, sedentary, want to get fit and build muscle",
        "Female, age 35, 5 ft 6 in, 140 lbs, very active, intermediate, goals: general fitness"
    ]

    profiles = []
    for text in test_cases:
        profile_obj = extractor.extract(text)
        profile_dict = profile_obj.to_dict()
        # Ensure all keys exist for consistency
        all_keys = [
            "age", "gender", "weight", "height", "bmi", "bmi_category",
            "fitness_level", "activity_level", "goals",
            "nutrition_preferences", "schedule_preferences",
            "medical_conditions", "equipment_available"
        ]
        for key in all_keys:
            if key not in profile_dict:
                profile_dict[key] = None if key not in ["medical_conditions", "equipment_available", "goals"] else []
        profiles.append(profile_dict)

    # Save to JSON
    with open("fitness_profiles.json", "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(profiles)} profiles to 'fitness_profiles.json'")

if __name__ == "__main__":
    main()
