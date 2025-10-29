"""
Variation Tools
Purpose: Solve direct, inverse, and joint variation problems.
Role: Finds the constant 'k' and computes values for variation relationships.
Dependencies: None (uses basic algebra)
"""

from langchain.tools import tool


@tool
def solve_variation(variation_type: str, known_values_json: str, target_variable: str) -> str:
    """
    Solves variation problems by finding constant 'k' and computing the target value.

    Supports direct, inverse, direct square, inverse square, and joint variations.

    Args:
        variation_type: Type of variation -
                       "direct": y = kx
                       "inverse": y = k/x
                       "direct_square": y = kx²
                       "inverse_square": y = k/x²
                       "joint": y = kxz (or more variables)
        known_values_json: JSON with known variable values.
                          Format: '{"y1": 3.08, "x1": 2.8, "y2": 19.25}' or
                                 '{"y1": 10, "x1": 2, "z1": 5, "x2": 4, "z2": 3}'
        target_variable: Variable to solve for (e.g., "x2", "y2")

    Returns:
        String with the solution and constant k

    Example:
        solve_variation("direct_square", '{"y1":3.08,"x1":2.8,"y2":19.25}', "x2")
    """
    try:
        import json

        known = json.loads(known_values_json)

        # Direct variation: y = kx
        if variation_type == "direct":
            if 'y1' in known and 'x1' in known:
                k = known['y1'] / known['x1']

                if target_variable == "y2" and 'x2' in known:
                    result = k * known['x2']
                    return f"k = {k}, {target_variable} = {result}"
                elif target_variable == "x2" and 'y2' in known:
                    result = known['y2'] / k
                    return f"k = {k}, {target_variable} = {result}"

        # Inverse variation: y = k/x
        elif variation_type == "inverse":
            if 'y1' in known and 'x1' in known:
                k = known['y1'] * known['x1']

                if target_variable == "y2" and 'x2' in known:
                    result = k / known['x2']
                    return f"k = {k}, {target_variable} = {result}"
                elif target_variable == "x2" and 'y2' in known:
                    result = k / known['y2']
                    return f"k = {k}, {target_variable} = {result}"

        # Direct square variation: y = kx²
        elif variation_type == "direct_square":
            if 'y1' in known and 'x1' in known:
                k = known['y1'] / (known['x1'] ** 2)

                if target_variable == "y2" and 'x2' in known:
                    result = k * (known['x2'] ** 2)
                    return f"k = {k}, {target_variable} = {result}"
                elif target_variable == "x2" and 'y2' in known:
                    result = (known['y2'] / k) ** 0.5
                    return f"k = {k}, {target_variable} = {result}"

        # Inverse square variation: y = k/x²
        elif variation_type == "inverse_square":
            if 'y1' in known and 'x1' in known:
                k = known['y1'] * (known['x1'] ** 2)

                if target_variable == "y2" and 'x2' in known:
                    result = k / (known['x2'] ** 2)
                    return f"k = {k}, {target_variable} = {result}"
                elif target_variable == "x2" and 'y2' in known:
                    result = (k / known['y2']) ** 0.5
                    return f"k = {k}, {target_variable} = {result}"

        # Joint variation: y = kxz
        elif variation_type == "joint":
            if 'y1' in known and 'x1' in known and 'z1' in known:
                k = known['y1'] / (known['x1'] * known['z1'])

                if target_variable == "y2" and 'x2' in known and 'z2' in known:
                    result = k * known['x2'] * known['z2']
                    return f"k = {k}, {target_variable} = {result}"

        return f"Error: Could not solve for {target_variable} with given values"

    except Exception as e:
        return f"Error solving variation: {str(e)}"
