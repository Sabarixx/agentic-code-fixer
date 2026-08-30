from typing import Dict, List

def is_valid(s: str) -> bool:
    """
    Return True if the input string s is a valid parentheses string.
    A string is valid when every opening bracket is closed by the same type
    of bracket in the correct order, and every closing bracket has a matching
    opening bracket.

    Parameters
    ----------
    s : str
        String consisting only of the characters '(', ')', '[', ']', '{', '}'.

    Returns
    -------
    bool
        True if s is a valid parentheses string, False otherwise.
    """
    # Quick rejection for odd length strings
    if len(s) % 2 == 1:
        return False

    # Mapping of closing to opening brackets
    pairs: Dict[str, str] = {')': '(', ']': '[', '}': '{'}
    stack: List[str] = []

    for ch in s:
        if ch in pairs.values():          # opening bracket
            stack.append(ch)
        else:                             # closing bracket
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()

    return not stack