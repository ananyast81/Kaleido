import html
import re
from functools import lru_cache

import spacy


# These are the entity types useful for news retrieval.
USEFUL_ENTITY_LABELS = {
    "PERSON",
    "ORG",
    "GPE",
    "LOC",
    "FAC",
    "EVENT",
    "PRODUCT",
    "DATE",
    "LAW",
    "NORP",
}


ENTITY_MEANINGS = {
    "PERSON": "Person",
    "ORG": "Organization",
    "GPE": "Country, city or state",
    "LOC": "Location",
    "FAC": "Building, airport or facility",
    "EVENT": "Named event",
    "PRODUCT": "Product",
    "DATE": "Date or period",
    "LAW": "Named law or regulation",
    "NORP": "Nationality, religious or political group",
}


# These lines commonly appear around an article but are not article content.
BOILERPLATE_LINES = {
    "advertisement",
    "read more",
    "subscribe",
    "sign up",
    "share this article",
    "follow us",
}


@lru_cache(maxsize=1)
def get_nlp():
    """
    Load the NLP model once and reuse it.

    Without caching, the model would be loaded again for every request,
    which would be slow and waste memory.
    """
    return spacy.load("en_core_web_sm")


def clean_article_text(text: str) -> str:
    """
    Remove repeated whitespace, HTML characters, duplicate lines
    and obvious boilerplate.
    """

    # Convert encoded characters such as &amp; into normal characters.
    text = html.unescape(text)

    # Replace non-breaking spaces with normal spaces.
    text = text.replace("\u00a0", " ")

    # Standardize newline characters.
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove repeated spaces and tabs while preserving newlines.
    text = re.sub(r"[ \t]+", " ", text)

    # Limit excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    cleaned_lines = []
    seen_lines = set()

    for raw_line in text.splitlines():
        line = raw_line.strip()

        # Ignore empty lines.
        if not line:
            continue

        normalized_line = line.casefold()

        # Ignore common page boilerplate.
        if normalized_line in BOILERPLATE_LINES:
            continue

        # Ignore duplicate substantial lines.
        if normalized_line in seen_lines and len(line) > 20:
            continue

        seen_lines.add(normalized_line)
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def process_article_text(text: str) -> dict:
    """
    Clean the text and run one spaCy pass to obtain both
    sentences and entities.
    """

    cleaned_text = clean_article_text(text)

    if len(cleaned_text) < 200:
        raise ValueError(
            "The extracted article content is too short to process."
        )

    nlp = get_nlp()

    # spaCy converts the text into a structured Doc object.
    doc = nlp(cleaned_text)

    sentences = []

    for sentence in doc.sents:
        sentence_text = re.sub(
            r"\s+",
            " ",
            sentence.text
        ).strip()

        # Very short pieces are often captions, labels or noise.
        if len(sentence_text.split()) >= 3:
            sentences.append(sentence_text)

    entities = []
    seen_entities = set()

    for entity in doc.ents:
        if entity.label_ not in USEFUL_ENTITY_LABELS:
            continue

        entity_text = re.sub(
            r"\s+",
            " ",
            entity.text
        ).strip()

        entity_key = (
            entity_text.casefold(),
            entity.label_
        )

        # Avoid returning the same entity repeatedly.
        if entity_key in seen_entities:
            continue

        seen_entities.add(entity_key)

        entities.append({
            "text": entity_text,
            "label": entity.label_,
            "meaning": ENTITY_MEANINGS.get(
                entity.label_,
                entity.label_
            ),
        })

    word_count = sum(
        1
        for token in doc
        if not token.is_space and not token.is_punct
    )

    return {
        "cleaned_text": cleaned_text,
        "sentences": sentences,
        "entities": entities,
        "sentence_count": len(sentences),
        "word_count": word_count,
    }