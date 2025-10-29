"""
Quadratic Tools
Purpose: Analyze quadratic functions and equations (ax² + bx + c).
Role: Solves quadratic equations, finds vertex, axis of symmetry, and extremum.
Dependencies: sympy for symbolic math
"""

from langchain.tools import tool
from typing import Dict, List, Union
import sympy as sp


@tool
def analyze_quadratic(a: float, b: float, c: float) -> str:
    """
    Analyzes a quadratic function f(x) = ax² + bx + c.

    Returns roots, vertex coordinates, axis of symmetry, and extremum type.
    Useful for word problems involving area, graphs, and optimization.

    Args:
        a: Coefficient of x² (must be non-zero)
        b: Coefficient of x
        c: Constant term

    Returns:
        String with JSON-formatted analysis containing:
        - roots: List of solutions to ax² + bx + c = 0
        - vertex: Dictionary with x and y coordinates of vertex
        - axis_of_symmetry: String equation of axis (x = h)
        - extremum_type: "Maximum" if a < 0, "Minimum" if a > 0

    Example:
        analyze_quadratic(-1, 6, -5) returns analysis for f(x) = -x² + 6x - 5
    """
    try:
        if a == 0:
            return "Error: Coefficient 'a' cannot be zero for a quadratic function"

        x = sp.Symbol('x')

        # Solve for roots
        equation = a * x**2 + b * x + c
        roots = sp.solve(equation, x)
        roots_list = [float(r.evalf()) for r in roots]

        # Calculate vertex (h, k) where h = -b/(2a)
        h = -b / (2 * a)
        k = a * h**2 + b * h + c

        # Determine extremum type
        extremum_type = "Maximum" if a < 0 else "Minimum"

        # Format result
        result = {
            "roots": roots_list,
            "vertex": {"x": round(h, 4), "y": round(k, 4)},
            "axis_of_symmetry": f"x = {round(h, 4)}",
            "extremum_type": extremum_type
        }

        import json
        return json.dumps(result, indent=2)

    except Exception as e:
        return f"Error analyzing quadratic: {str(e)}"


@tool
def solve_quadratic_equation(a: float, b: float, c: float) -> str:
    """
    Solves the quadratic equation ax² + bx + c = 0.

    Args:
        a: Coefficient of x² (must be non-zero)
        b: Coefficient of x
        c: Constant term

    Returns:
        String listing the roots/solutions

    Example:
        solve_quadratic_equation(1, -5, 6) solves x² - 5x + 6 = 0
    """
    try:
        if a == 0:
            return "Error: Coefficient 'a' cannot be zero for a quadratic equation"

        x = sp.Symbol('x')
        equation = a * x**2 + b * x + c
        roots = sp.solve(equation, x)

        if len(roots) == 0:
            return "No real solutions"
        elif len(roots) == 1:
            return f"One solution: x = {float(roots[0].evalf())}"
        else:
            root_values = [float(r.evalf()) for r in roots]
            return f"Solutions: x = {root_values[0]}, x = {root_values[1]}"

    except Exception as e:
        return f"Error solving equation: {str(e)}"


@tool
def find_quadratic_vertex(a: float, b: float, c: float) -> str:
    """
    Finds the vertex (turning point) of a quadratic function.

    Args:
        a: Coefficient of x²
        b: Coefficient of x
        c: Constant term

    Returns:
        String with vertex coordinates (h, k)

    Example:
        find_quadratic_vertex(-1, 6, -5) finds vertex of f(x) = -x² + 6x - 5
    """
    try:
        if a == 0:
            return "Error: Coefficient 'a' cannot be zero"

        h = -b / (2 * a)
        k = a * h**2 + b * h + c

        return f"Vertex: ({round(h, 4)}, {round(k, 4)})"

    except Exception as e:
        return f"Error finding vertex: {str(e)}"
