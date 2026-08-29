from typing import Dict, List

def is_valid(s: str) -> bool:
    """
    Determine if the input string s is a valid parentheses string.

    A string is valid if every opening bracket is closed by the same type of
    bracket in the correct order, and every closing bracket has a matching
    opening bracket.

    Parameters
    ----------
    s : str
        The string to validate, consisting only of '()[]{}'.

    Returns
    -------
    bool
        True if s is a valid parentheses string, False otherwise.
    """
    # Quick check: odd length cannot be valid
    if len(s) % 2 == 1:
        return False

    # Mapping of closing to opening brackets
    pairs: Dict[str, str] = {')': '(', ']': '[', '}': '{'}
    stack: List[str] = []

    for ch in s:
        if ch in pairs.values():          # opening bracket
            stack.append(ch)
        elif ch in pairs:                 # closing bracket
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
        else:
            # Invalid character (should not happen per constraints)
            return False

    return not stack