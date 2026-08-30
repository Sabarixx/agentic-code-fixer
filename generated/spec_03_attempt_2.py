from typing import Dict, List

def is_valid(s: str) -> bool:
    """
    Check whether a string of brackets is syntactically correct.

    A string is valid if every opening bracket has a matching closing
    bracket of the same type and the brackets are properly nested.

    Parameters
    ----------
    s : str
        String containing only '(', ')', '[', ']', '{', '}'.

    Returns
    -------
    bool
        True if the string is a valid bracket sequence, False otherwise.
    """
    # Map closing brackets to their corresponding opening brackets
    closing_to_opening: Dict[str, str] = {')': '(', ']': '[', '}': '{'}
    opening_brackets = set(closing_to_opening.values())

    stack: List[str] = []

    for char in s:
        if char in opening_brackets:
            stack.append(char)
        elif char in closing_to_opening:
            if not stack or stack.pop() != closing_to_opening[char]:
                return False
        else:
            # Unexpected character – invalid input
            return False

    return not stack