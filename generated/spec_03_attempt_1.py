from typing import Dict, List

def is_valid(s: str) -> bool:
    """
    Return True if s is a valid parentheses string.
    A string is valid when open brackets are closed by the same type of brackets,
    in the correct order, and every close has a matching open.

    Parameters
    ----------
    s : str
        String consisting only of '()[]{}'.

    Returns
    -------
    bool
        True if the string is valid, False otherwise.
    """
    # Mapping of closing to opening brackets
    pairs: Dict[str, str] = {')': '(', ']': '[', '}': '{'}
    stack: List[str] = []

    for ch in s:
        if ch in pairs.values():  # opening bracket
            stack.append(ch)
        elif ch in pairs:  # closing bracket
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
        else:
            # Invalid character (should not happen per constraints)
            return False

    return not stack