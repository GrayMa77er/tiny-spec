# Ticket: top-N word frequencies

Implement a function that returns the most frequent words in a piece of text.

## Public API (grading imports this exactly)
- File: `solution.py` at the project root.
- Function: `top_words(text: str, n: int) -> list[tuple[str, int]]`

## Behaviour
- A "word" is a maximal run of ASCII alphanumeric characters (`a`–`z`, `0`–`9`). Everything else (spaces, punctuation) is a separator.
- Counting is **case-insensitive**: words are lowercased before counting.
- Return the top `n` words as a list of `(word, count)` tuples, ordered by **count descending**; ties broken by the word **alphabetically ascending**.
- If `n` exceeds the number of distinct words, return them all. If the text has no words, return an empty list.

## Examples
- `top_words("the quick brown fox the lazy dog the fox", 2)` → `[("the", 3), ("fox", 2)]`
- `top_words("the quick brown fox the lazy dog the fox", 3)` → `[("the", 3), ("fox", 2), ("brown", 1)]`  (the 1-count words tie, so `brown` wins alphabetically)
- `top_words("Hello, hello! World.", 1)` → `[("hello", 2)]`

Acceptance: correct counts, case-insensitive tokenization, count-desc ordering with alphabetical tie-breaking, and correct handling of `n` larger than the vocabulary.
