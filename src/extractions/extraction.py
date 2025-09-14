import sys
import json

def extract(text):
    return {
        "age": None,
        "weight": None,
        "height": None,
        "nutrition": None,
        "goal": None,
        "schedule": None,
        "gender": None,
        "confidence": {},
        "source": {}
    }

if __name__ == "__main__":
    input_text = sys.argv[1]
    result = extract(input_text)
    print(json.dumps(result, indent=2, ensure_ascii=False))
