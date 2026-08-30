from typing import Dict, List


def is_valid(s: str) -> bool:
    """
    Determine whether a string of brackets is properly nested.

    A string is valid if every opening bracket has a matching closing
    bracket of the same type and the brackets are correctly ordered.

    Parameters
    ----------
    s : str
        String containing only '(', ')', '[', ']', '{', '}'.

    Returns
    -------
    bool
        True if the string is a valid bracket sequence, False otherwise.
    """
    # A valid sequence must have an even length
    if len(s) % 2:
        return False

    # Map each closing bracket to its corresponding opening bracket
    closing_to_open: Dict[str, str] = {")": "(", "]": "[", "}": "{"}
    opening_brackets = set(closing_to_open.values())

    stack: List[str] = []

    for char in s:
        if char in opening_brackets:
            stack.append(char)
        else:  # char is a closing bracket
            if not stack or stack[-1] != closing_to_open[char]:
                return False
            stack.pop()

    return not stack