# Classify currently viewed article in the range (left - right) by assigning a score (0-1)
from functools import lru_cache
import os
import re


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
    if os.getenv("KALEIDO_ENABLE_BIAS_MODEL", "").lower() not in {"1", "true", "yes"}:
        words = set(re.findall(r"[a-z]+", text.casefold()))
        left_terms = {"climate", "union", "workers", "welfare", "equality"}
        right_terms = {"border", "tax", "crime", "military", "自由"}
        left_score = len(words & left_terms)
        right_score = len(words & right_terms)
        if left_score > right_score:
            return "left", 0.55
        if right_score > left_score:
            return "right", 0.55
        return "center", 0.4
    try:
        result = get_classifier()(text, truncation=True)[0]
    except Exception:
        return "center", 0.0
    return LABEL_MAP.get(result["label"], "center"), float(result["score"])