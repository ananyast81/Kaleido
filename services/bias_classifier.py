# Classify currently viewed article in the range (left - right) by assigning a score (0-1)
from transformers import pipeline

pipe = pipeline(
    "text-classification",
    model="matous-volf/political-leaning-politics",
    tokenizer="launch/POLITICS"
)

LABEL_MAP = {"LABEL_0": "left", "LABEL_1": "right", "LABEL_2": "right"}

def classify_bias(text: str) -> tuple[str, float]:
    result = pipe(text, truncation=True)[0]
    label = LABEL_MAP[result["label"]]
    confidence = result["score"]
    return label, confidence