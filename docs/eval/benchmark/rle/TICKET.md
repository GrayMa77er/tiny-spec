# Ticket: run-length encode / decode

Implement run-length encoding and its exact inverse for strings of lowercase letters.

## Public API (grading imports these exactly)
- File: `solution.py` at the project root.
- Functions: `encode(s: str) -> str` and `decode(s: str) -> str`

## Behaviour
- Input to `encode` is a string of lowercase letters `a`–`z` (possibly empty).
- `encode` replaces each maximal run of one repeated character with `<count><char>`. The count is **always written**, even when it is 1. Counts may be multiple digits.
- `decode` is the exact inverse: `decode(encode(s)) == s` for every valid input.
- `encode("")` returns `""`.

## Examples
- `encode("aaab")` → `"3a1b"`
- `encode("abc")` → `"1a1b1c"`
- `encode("aaaaaaaaaab")` → `"10a1b"`
- `decode("3a1b")` → `"aaab"`

Acceptance: encode produces the count-prefixed form, and decode round-trips every input exactly (including multi-digit run lengths).
