# Classify currently viewed article in the range (left - right) by assigning a score (0-1)
from functools import lru_cache


LABEL_MAP = {"LABEL_0": "left", "LABEL_1": "center", "LABEL_2": "right"}


@lru_cache(maxsize=1)
def get_classifier():
    from transformers import pipeline
    return pipeline(
        "text-classification",
        model="matous-volf/political-leaning-politics",
        tokenizer="launch/POLITICS",
    )


def classify_bias(text: str) -> tuple[str, float]:
    if not text.strip():
        return "center", 0.0
    try:
        result = get_classifier()(text, truncation=True)[0]
    except Exception:
        return "center", 0.0
    return LABEL_MAP.get(result["label"], "center"), float(result["score"])