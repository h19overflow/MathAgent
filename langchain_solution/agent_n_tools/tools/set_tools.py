"""
Set Operations and Venn Diagram Tools
Purpose: Solve problems involving Venn diagrams and set operations.
Role: Solves for unknowns in Venn diagrams using set cardinality equations.
Dependencies: sympy for symbolic equation solving
"""

from langchain.tools import tool
import sympy as sp


@tool
def solve_venn_diagram(regions_json: str, equation: str, variable: str = "x") -> str:
    """
    Solves for an unknown variable in a Venn diagram.

    Used when regions contain algebraic expressions and you need to find the variable
    based on total elements or relationships between sets.

    Args:
        regions_json: JSON string with region labels and values/expressions.
                     Format: '{"J_only": 7, "J_and_K": 2, "K_only": "x+2", ...}'
        equation: The equation to solve (e.g., "7 + 2 + x+2 + 3 + x+5 = 25")
        variable: The variable to solve for (default: "x")

    Returns:
        String with the solution for the variable

    Example:
        solve_venn_diagram('{"J_only": 7, "K_only": "x+2"}', '7 + x+2 = 15', 'x')
    """
    try:
        import json

        var = sp.Symbol(variable)

        # Parse and solve the equation
        eq = sp.sympify(equation)
        solutions = sp.solve(eq, var)

        if len(solutions) == 0:
            return f"No solution found for {variable}"
        elif len(solutions) == 1:
            return f"Solution: {variable} = {float(solutions[0].evalf())}"
        else:
            sols = [float(s.evalf()) for s in solutions]
            return f"Multiple solutions for {variable}: {sols}"

    except Exception as e:
        return f"Error solving Venn diagram: {str(e)}"


@tool
def calculate_set_union(set_a_json: str, set_b_json: str) -> str:
    """
    Calculates the union of two sets (A ∪ B).

    Args:
        set_a_json: JSON string list of elements in set A (e.g., '[1, 2, 3]')
        set_b_json: JSON string list of elements in set B (e.g., '[3, 4, 5]')

    Returns:
        String with the union set

    Example:
        calculate_set_union('[1, 2, 3]', '[3, 4, 5]') returns {1, 2, 3, 4, 5}
    """
    try:
        import json

        set_a = set(json.loads(set_a_json))
        set_b = set(json.loads(set_b_json))

        union = set_a.union(set_b)

        return f"A ∪ B = {sorted(list(union))}"

    except Exception as e:
        return f"Error calculating union: {str(e)}"


@tool
def calculate_set_intersection(set_a_json: str, set_b_json: str) -> str:
    """
    Calculates the intersection of two sets (A ∩ B).

    Args:
        set_a_json: JSON string list of elements in set A
        set_b_json: JSON string list of elements in set B

    Returns:
        String with the intersection set

    Example:
        calculate_set_intersection('[1, 2, 3]', '[3, 4, 5]') returns {3}
    """
    try:
        import json

        set_a = set(json.loads(set_a_json))
        set_b = set(json.loads(set_b_json))

        intersection = set_a.intersection(set_b)

        return f"A ∩ B = {sorted(list(intersection))}"

    except Exception as e:
        return f"Error calculating intersection: {str(e)}"


@tool
def calculate_set_difference(set_a_json: str, set_b_json: str) -> str:
    """
    Calculates the difference of two sets (A - B or A \ B).

    Returns elements in A but not in B.

    Args:
        set_a_json: JSON string list of elements in set A
        set_b_json: JSON string list of elements in set B

    Returns:
        String with the difference set

    Example:
        calculate_set_difference('[1, 2, 3, 4]', '[3, 4, 5]') returns {1, 2}
    """
    try:
        import json

        set_a = set(json.loads(set_a_json))
        set_b = set(json.loads(set_b_json))

        difference = set_a.difference(set_b)

        return f"A - B = {sorted(list(difference))}"

    except Exception as e:
        return f"Error calculating difference: {str(e)}"


@tool
def calculate_set_complement(universal_set_json: str, set_a_json: str) -> str:
    """
    Calculates the complement of a set A with respect to a universal set.

    Returns elements in the universal set but not in A.

    Args:
        universal_set_json: JSON string list of all elements in universal set
        set_a_json: JSON string list of elements in set A

    Returns:
        String with the complement set (A')

    Example:
        calculate_set_complement('[1,2,3,4,5]', '[2,4]') returns {1, 3, 5}
    """
    try:
        import json

        universal = set(json.loads(universal_set_json))
        set_a = set(json.loads(set_a_json))

        complement = universal.difference(set_a)

        return f"A' = {sorted(list(complement))}"

    except Exception as e:
        return f"Error calculating complement: {str(e)}"
