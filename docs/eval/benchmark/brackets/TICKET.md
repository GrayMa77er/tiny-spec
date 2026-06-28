# Ticket: balanced brackets checker

Implement a function that reports whether the brackets in a string are balanced.

## Public API (grading imports this exactly)
- File: `solution.py` at the project root.
- Function: `is_balanced(s: str) -> bool`

## Behaviour
- Consider three bracket pairs: `()`, `[]`, `{}`.
- Return `True` if every opening bracket is closed by the matching type in the correct order, and `False` otherwise.
- Any non-bracket characters are ignored.
- The empty string is balanced (`True`).

## Examples
- `is_balanced("()")` → `True`
- `is_balanced("([{}])")` → `True`
- `is_balanced("a(b)c[d]{e}")` → `True`
- `is_balanced("([)]")` → `False`
- `is_balanced("(")` → `False`

Acceptance: correctly handles nesting, interleaving, unclosed and unopened brackets, and mismatched types.
