from services.chunker import (
    count_tokens,
    get_tokenizer,
)


sample_text = (
    "Microsoft announced a new artificial "
    "intelligence investment in India."
)


print("Loading tokenizer...")

tokenizer = get_tokenizer()

print("\nTokenizer loaded successfully.")

print(
    "Tokenizer class:",
    type(tokenizer).__name__,
)

print(
    "Model name:",
    tokenizer.name_or_path,
)

print(
    "Special tokens:",
    tokenizer.special_tokens_map,
)

print(
    "Special-token count:",
    tokenizer.num_special_tokens_to_add(
        pair=False
    ),
)

print(
    "Normal tokens:",
    tokenizer.tokenize(sample_text),
)

print(
    "Token IDs:",
    tokenizer.encode(
        sample_text,
        add_special_tokens=True,
    ),
)

print(
    "Total token count:",
    count_tokens(sample_text),
)

same_tokenizer = tokenizer is get_tokenizer()

print(
    "Tokenizer reused from memory:",
    same_tokenizer,
)

print(
    "Cache information:",
    get_tokenizer.cache_info(),
)