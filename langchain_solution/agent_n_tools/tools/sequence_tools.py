"""
Sequence Analysis Tools
Purpose: Analyze arithmetic and geometric progressions.
Role: Identifies sequence patterns and generates formulas for nth terms.
Dependencies: None (uses basic arithmetic)
"""

from langchain.tools import tool
from typing import List


@tool
def analyze_sequence(sequence_json: str) -> str:
    """
    Analyzes a number sequence to identify if it's an arithmetic or geometric progression.

    Returns the sequence type, first term, common difference/ratio, and nth term formula.

    Args:
        sequence_json: JSON string list of numbers (e.g., '[3, 5, 7, 9]' or '[2, 6, 18, 54]')

    Returns:
        String with JSON-formatted analysis containing:
        - type: "Arithmetic Progression" or "Geometric Progression" or "Unknown"
        - first_term_a: First term of the sequence
        - common_difference_d or common_ratio_r: The pattern parameter
        - nth_term_formula: Formula for the nth term

    Example:
        analyze_sequence('[3, 5, 7, 9]') identifies arithmetic progression with d=2
    """
    try:
        import json

        sequence = json.loads(sequence_json)

        if not isinstance(sequence, list) or len(sequence) < 2:
            return "Error: Sequence must be a list with at least 2 numbers"

        sequence = [float(x) for x in sequence]
        n = len(sequence)

        # Check for Arithmetic Progression
        differences = [sequence[i+1] - sequence[i] for i in range(n-1)]
        is_ap = all(abs(d - differences[0]) < 1e-9 for d in differences)

        if is_ap:
            a = sequence[0]
            d = differences[0]
            # Formula: Tn = a + (n-1)d
            if d == 0:
                formula = f"{a}"
            elif d == 1:
                formula = f"{a} + (n-1)" if a != 1 else "n"
                if a == 0:
                    formula = "n - 1"
                elif a == 1:
                    formula = "n"
                else:
                    formula = f"{d}n + {a - d}"
            else:
                # Simplify to form: dn + (a-d)
                formula = f"{d}n + {a - d}"

            result = {
                "type": "Arithmetic Progression",
                "first_term_a": a,
                "common_difference_d": d,
                "nth_term_formula": formula
            }
            return json.dumps(result, indent=2)

        # Check for Geometric Progression
        ratios = [sequence[i+1] / sequence[i] if sequence[i] != 0 else None for i in range(n-1)]
        if None not in ratios:
            is_gp = all(abs(r - ratios[0]) < 1e-9 for r in ratios if r is not None)

            if is_gp:
                a = sequence[0]
                r = ratios[0]
                # Formula: Tn = a * r^(n-1)
                formula = f"{a} * {r}^(n-1)"

                result = {
                    "type": "Geometric Progression",
                    "first_term_a": a,
                    "common_ratio_r": r,
                    "nth_term_formula": formula
                }
                return json.dumps(result, indent=2)

        # Unknown pattern
        result = {
            "type": "Unknown",
            "message": "Sequence does not follow a simple arithmetic or geometric pattern"
        }
        return json.dumps(result, indent=2)

    except Exception as e:
        return f"Error analyzing sequence: {str(e)}"


@tool
def find_nth_term(sequence_json: str, n: int) -> str:
    """
    Finds the nth term of an arithmetic or geometric sequence.

    Args:
        sequence_json: JSON string list of at least 2 numbers (e.g., '[3, 5, 7]')
        n: The term number to find (must be positive)

    Returns:
        String with the nth term value

    Example:
        find_nth_term('[3, 5, 7, 9]', 8) finds the 8th term
    """
    try:
        import json

        sequence = json.loads(sequence_json)
        sequence = [float(x) for x in sequence]

        if n <= 0:
            return "Error: n must be a positive integer"

        if len(sequence) < 2:
            return "Error: Sequence must have at least 2 numbers"

        # Check if AP
        differences = [sequence[i+1] - sequence[i] for i in range(len(sequence)-1)]
        is_ap = all(abs(d - differences[0]) < 1e-9 for d in differences)

        if is_ap:
            a = sequence[0]
            d = differences[0]
            # Tn = a + (n-1)d
            term_n = a + (n - 1) * d
            return f"Term {n} of the sequence: {term_n}"

        # Check if GP
        ratios = [sequence[i+1] / sequence[i] if sequence[i] != 0 else None for i in range(len(sequence)-1)]
        if None not in ratios:
            is_gp = all(abs(r - ratios[0]) < 1e-9 for r in ratios)

            if is_gp:
                a = sequence[0]
                r = ratios[0]
                # Tn = a * r^(n-1)
                term_n = a * (r ** (n - 1))
                return f"Term {n} of the sequence: {term_n}"

        return "Error: Sequence does not follow AP or GP pattern"

    except Exception as e:
        return f"Error finding nth term: {str(e)}"
