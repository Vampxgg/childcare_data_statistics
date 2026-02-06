# -*- coding: utf-8 -*-
"""
节点ID: 1766335411658
节点标题: 代码执行 22
节点描述: 
节点类型: code
"""

def main(arg1: str):
    """
    Removes all occurrences of '---' from the input string arg1.

    If an error occurs during the processing, the original string arg1 is returned.
    If successful, the modified string (with '---' removed) is returned.

    Args:
        arg1: The input string.

    Returns:
        A dictionary with a single key 'result' whose value is
        the processed string or the original string if an error occurred.
    """
    # Initialize the result with the original arg1.
    # This covers the "return original on error" case by default.
    result_value = arg1

    try:
        # Perform the string replacement.
        # The .replace() method replaces all occurrences of the first argument
        # with the second argument. It's a robust method that typically
        # doesn't raise errors for valid string inputs.
        updated_arg1 = arg1.replace("---", "")

        # If the replacement was successful (which it almost always will be
        # when arg1 is a string), update the result_value.
        result_value = updated_arg1

    except Exception as e:
        # In the unlikely event of an error (e.g., if arg1 somehow wasn't
        # a string despite the type hint, or for extremely rare system-level issues),
        # we catch the exception.
        # The result_value remains arg1 as it was initialized, fulfilling
        # the requirement to return the original on error.
        # print(f"An error occurred during string replacement: {e}. Returning original arg1.")
        pass # No explicit action needed here, as result_value is already arg1

    return {
        "result": result_value
    }

