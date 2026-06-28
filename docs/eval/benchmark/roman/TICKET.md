# Ticket: integer → Roman numeral

Implement a function that converts an integer to its Roman numeral string.

## Public API (grading imports this exactly)
- File: `solution.py` at the project root.
- Function: `to_roman(n: int) -> str`

## Behaviour
- Input is an integer in the range **1 to 3999** inclusive.
- Return the standard Roman numeral, using subtractive notation (4 = `IV`, 9 = `IX`, 40 = `XL`, 90 = `XC`, 400 = `CD`, 900 = `CM`).

## Examples
- `to_roman(3)` → `"III"`
- `to_roman(4)` → `"IV"`
- `to_roman(58)` → `"LVIII"`
- `to_roman(1994)` → `"MCMXCIV"`

Acceptance: the function returns the correct numeral across the full range, including all the subtractive cases.
