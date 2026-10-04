from functools import lru_cache

from transformers import AutoTokenizer


TOKENIZER_MODEL_NAME = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

DEFAULT_MAX_TOKENS = 120
DEFAULT_OVERLAP_SENTENCES = 1


@lru_cache(maxsize=1)
def get_tokenizer():
    """
    Load the tokenizer once and reuse it for every article.
    """
    return AutoTokenizer.from_pretrained(
        TOKENIZER_MODEL_NAME
    )


def count_tokens(text: str) -> int:
    """
    Return the number of tokens the embedding model's
    tokenizer creates for the supplied text.
    """
    tokenizer = get_tokenizer()

    token_ids = tokenizer.encode(
        text,
        add_special_tokens=True,
        truncation=False,
    )

    return len(token_ids)


def split_oversized_sentence(
    sentence: str,
    sentence_index: int,
    max_tokens: int,
) -> list[dict]:
    """
    Handle an unusually long sentence that exceeds the
    complete chunk limit.

    Normal sentences remain intact. Only an oversized
    sentence is divided.
    """
    tokenizer = get_tokenizer()

    special_token_count = (
        tokenizer.num_special_tokens_to_add(pair=False)
    )

    available_tokens = max_tokens - special_token_count

    if available_tokens <= 0:
        raise ValueError(
            "max_tokens is too small for this tokenizer."
        )

    token_ids = tokenizer.encode(
        sentence,
        add_special_tokens=False,
        truncation=False,
    )

    sentence_parts = []

    for start in range(
        0,
        len(token_ids),
        available_tokens,
    ):
        part_ids = token_ids[
            start:start + available_tokens
        ]

        part_text = tokenizer.decode(
            part_ids,
            skip_special_tokens=True,
        ).strip()

        if part_text:
            sentence_parts.append({
                "text": part_text,
                "sentence_index": sentence_index,
            })

    return sentence_parts


def get_chunk_entities(
    chunk_text: str,
    entities: list[dict],
) -> list[dict]:
    """
    Keep only entities that actually appear in this chunk.
    """
    normalized_chunk = chunk_text.casefold()
    chunk_entities = []

    for entity in entities:
        entity_text = entity["text"].strip()

        if entity_text.casefold() in normalized_chunk:
            chunk_entities.append(entity)

    return chunk_entities


def build_chunk(
    article_id: str,
    chunk_index: int,
    sentence_units: list[dict],
    entities: list[dict],
) -> dict:
    """
    Convert a group of sentence units into one final chunk.
    """
    chunk_text = " ".join(
        unit["text"]
        for unit in sentence_units
    ).strip()

    sentence_indexes = [
        unit["sentence_index"]
        for unit in sentence_units
    ]

    return {
        "chunk_id": (
            f"{article_id}-chunk-{chunk_index}"
        ),
        "text": chunk_text,
        "token_count": count_tokens(chunk_text),
        "start_sentence": min(sentence_indexes),
        "end_sentence": max(sentence_indexes),
        "entities": get_chunk_entities(
            chunk_text,
            entities,
        ),
    }


def create_chunks(
    article_id: str,
    sentences: list[str],
    entities: list[dict],
    max_tokens: int = DEFAULT_MAX_TOKENS,
    overlap_sentences: int = (
        DEFAULT_OVERLAP_SENTENCES
    ),
) -> list[dict]:
    """
    Group complete sentences until adding another sentence
    would exceed max_tokens.

    The last sentence of the previous chunk is reused as
    context in the next chunk.
    """
    if max_tokens < 20:
        raise ValueError(
            "max_tokens must be at least 20."
        )

    if overlap_sentences < 0:
        raise ValueError(
            "overlap_sentences cannot be negative."
        )

    sentence_units = []

    # Prepare every sentence for chunking.
    for sentence_index, sentence in enumerate(sentences):
        sentence = sentence.strip()

        if not sentence:
            continue

        if count_tokens(sentence) <= max_tokens:
            sentence_units.append({
                "text": sentence,
                "sentence_index": sentence_index,
            })
        else:
            # Only very long sentences are divided.
            sentence_units.extend(
                split_oversized_sentence(
                    sentence=sentence,
                    sentence_index=sentence_index,
                    max_tokens=max_tokens,
                )
            )

    if not sentence_units:
        return []

    chunks = []
    current_units = []

    for unit in sentence_units:
        candidate_units = current_units + [unit]

        candidate_text = " ".join(
            item["text"]
            for item in candidate_units
        )

        candidate_token_count = count_tokens(
            candidate_text
        )

        # The new sentence still fits in the current chunk.
        if (
            not current_units
            or candidate_token_count <= max_tokens
        ):
            current_units.append(unit)
            continue

        # The new sentence does not fit, so finish the
        # current chunk first.
        chunks.append(
            build_chunk(
                article_id=article_id,
                chunk_index=len(chunks),
                sentence_units=current_units,
                entities=entities,
            )
        )

        # Copy the last sentence into the next chunk.
        if overlap_sentences > 0:
            current_units = current_units[
                -overlap_sentences:
            ]
        else:
            current_units = []

        # If the overlap plus the new sentence is too large,
        # discard overlap until the new sentence fits.
        while current_units:
            overlap_candidate = " ".join(
                item["text"]
                for item in current_units + [unit]
            )

            if (
                count_tokens(overlap_candidate)
                <= max_tokens
            ):
                break

            current_units.pop(0)

        current_units.append(unit)

    # Store the final unfinished chunk.
    if current_units:
        final_chunk = build_chunk(
            article_id=article_id,
            chunk_index=len(chunks),
            sentence_units=current_units,
            entities=entities,
        )

        # Prevent an overlap-only duplicate chunk.
        if (
            not chunks
            or final_chunk["text"] != chunks[-1]["text"]
        ):
            chunks.append(final_chunk)

    return chunks