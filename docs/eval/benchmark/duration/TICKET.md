# Ticket: parse a duration string into seconds

Implement a function that parses a compact duration string into a total number of seconds.

## Public API (grading imports this exactly)
- File: `solution.py` at the project root.
- Function: `parse_duration(s: str) -> int`

## Behaviour
- The string is one or more `<integer><unit>` segments concatenated, where unit is `h` (hours), `m` (minutes), or `s` (seconds). Example: `"1h30m15s"`.
- Return the total number of seconds as an int.
- The **entire** string must be valid. On any invalid input — empty string, unknown unit, a number with no unit, stray characters, negative numbers — raise `ValueError`.

## Examples
- `parse_duration("45s")` → `45`
- `parse_duration("2m")` → `120`
- `parse_duration("1h30m")` → `5400`
- `parse_duration("1h30m15s")` → `5415`
- `parse_duration("90m")` → `5400`
- `parse_duration("1h2")` → raises `ValueError`
- `parse_duration("")` → raises `ValueError`

Acceptance: valid strings return the correct second count; every invalid form raises `ValueError`.
