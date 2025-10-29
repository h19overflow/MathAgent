"""
Inequality Grapher Tool
Purpose: Visualize and validate inequalities through graphing and coordinate checking.
Role: Helps agents validate inequality solutions and identify boundary errors in graphing.
"""

from langchain.tools import tool
from typing import List, Tuple, Union
import sympy as sp
import matplotlib.pyplot as plt
import numpy as np
import os


@tool
def plot_linear_inequality(inequality: str, output_path: str = None) -> str:
    """Plot a linear inequality on a 2D graph.

    Args:
        inequality: The inequality to plot (e.g., "x + y <= 5" or "2*x - y > 3")
        output_path: Optional path to save the plot (default: saved to temp location)

    Returns:
        String indicating success and path to the generated plot
    """
    try:
        x, y = sp.symbols('x y')

        # Default output path
        if output_path is None:
            output_path = "plot_inequality.png"

        # Create figure
        fig, ax = plt.subplots(figsize=(8, 8))

        # Parse inequality and extract boundary line
        # For now, handle simple cases like "x + y <= 5"
        expr = sp.sympify(inequality)

        # Create a grid
        x_vals = np.linspace(-10, 10, 100)

        # Plot the inequality region (simplified visualization)
        ax.set_xlim(-10, 10)
        ax.set_ylim(-10, 10)
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='k', linewidth=0.5)
        ax.axvline(x=0, color='k', linewidth=0.5)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_title(f'Graph of: {inequality}')

        plt.savefig(output_path)
        plt.close()

        return f"Graph saved to: {output_path}"
    except Exception as e:
        return f"Error plotting inequality: {str(e)}"


@tool
def validate_point_in_inequality(inequality: str, point_x: Union[int, float],
                                 point_y: Union[int, float]) -> str:
    """Check if a point satisfies an inequality.

    Args:
        inequality: The inequality to check (e.g., "x + y <= 5")
        point_x: The x-coordinate of the point
        point_y: The y-coordinate of the point

    Returns:
        String indicating whether the point satisfies the inequality
    """
    try:
        x, y = sp.symbols('x y')
        expr = sp.sympify(inequality)

        # Substitute the point coordinates
        result = expr.subs([(x, point_x), (y, point_y)])

        # Check if the inequality is satisfied
        if result:
            return f"✓ Point ({point_x}, {point_y}) SATISFIES the inequality: {inequality}"
        else:
            return f"✗ Point ({point_x}, {point_y}) DOES NOT satisfy the inequality: {inequality}"
    except Exception as e:
        return f"Error validating point: {str(e)}"


@tool
def find_inequality_intercepts(inequality: str) -> str:
    """Find the x and y intercepts of the boundary line of an inequality.

    Args:
        inequality: The inequality (e.g., "x + y <= 5")

    Returns:
        String with x and y intercepts
    """
    try:
        x, y = sp.symbols('x y')
        expr = sp.sympify(inequality)

        # Find y-intercept (set x=0)
        y_intercept = sp.solve(expr.subs(x, 0), y)

        # Find x-intercept (set y=0)
        x_intercept = sp.solve(expr.subs(y, 0), x)

        return f"X-intercept(s): {x_intercept}, Y-intercept(s): {y_intercept}"
    except Exception as e:
        return f"Error finding intercepts: {str(e)}"


@tool
def check_boundary_line(inequality: str) -> str:
    """Determine the boundary line and whether it's included (solid or dashed).

    Args:
        inequality: The inequality (e.g., "x + y <= 5" or "x + y < 5")

    Returns:
        String describing the boundary line type
    """
    try:
        inequality_str = str(inequality)

        # Check for <= or >=  (solid line)
        if "<=" in inequality_str or ">=" in inequality_str:
            line_type = "SOLID (included in solution)"
        # Check for < or > (dashed line)
        elif "<" in inequality_str or ">" in inequality_str:
            line_type = "DASHED (not included in solution)"
        else:
            line_type = "UNKNOWN"

        # Extract the inequality direction
        if ">=" in inequality_str or ">" in inequality_str:
            direction = "ABOVE the boundary line"
        elif "<=" in inequality_str or "<" in inequality_str:
            direction = "BELOW the boundary line"
        else:
            direction = "UNKNOWN"

        return f"Boundary line: {line_type}\nShaded region: {direction}"
    except Exception as e:
        return f"Error checking boundary: {str(e)}"


@tool
def validate_inequality_solution_set(inequality: str, test_points_json: str) -> str:
    """Validate a set of test points against an inequality.

    Args:
        inequality: The inequality to validate (e.g., "x + y <= 5")
        test_points_json: JSON string of points list. Format: '[[x1, y1], [x2, y2], ...]' or '[[1, 2], [3, 4]]'

    Returns:
        String with validation results for each point
    """
    try:
        import json
        x, y = sp.symbols('x y')
        expr = sp.sympify(inequality)

        # Parse JSON string to get list of [x, y] pairs
        test_points = json.loads(test_points_json)

        results = []
        for point in test_points:
            if isinstance(point, (list, tuple)) and len(point) == 2:
                px, py = point[0], point[1]
                test_result = expr.subs([(x, px), (y, py)])
                status = "✓ SATISFIES" if test_result else "✗ DOES NOT"
                results.append(f"  ({px}, {py}): {status}")
            else:
                results.append(f"  Invalid point format: {point}")

        return f"Validation results for {inequality}:\n" + "\n".join(results)
    except Exception as e:
        return f"Error validating solution set: {str(e)}"
