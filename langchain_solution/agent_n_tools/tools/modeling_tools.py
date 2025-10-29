"""
Mathematical Modeling Tools
Purpose: Fit mathematical models to data (quadratic, linear, etc.).
Role: Determines equation parameters from given points and constraints.
Dependencies: sympy for symbolic solving
"""

from langchain.tools import tool
import sympy as sp


@tool
def fit_quadratic_model(vertex_json: str, point_json: str) -> str:
    """
    Determines the equation of a parabola y = a(x-h)² + k given its vertex and another point.

    Args:
        vertex_json: JSON dict with vertex coordinates.
                    Format: '{"x": 2, "y": 3}' where vertex is (h, k) = (2, 3)
        point_json: JSON dict with another point on the parabola.
                   Format: '{"x": 4, "y": 7}'

    Returns:
        String with the parabola equation

    Example:
        fit_quadratic_model('{"x":2,"y":3}', '{"x":4,"y":7}')
    """
    try:
        import json

        vertex = json.loads(vertex_json)
        point = json.loads(point_json)

        h = vertex['x']
        k = vertex['y']
        x_p = point['x']
        y_p = point['y']

        # Parabola form: y = a(x - h)² + k
        # Substitute the point to find 'a'
        # y_p = a(x_p - h)² + k
        # a = (y_p - k) / (x_p - h)²

        denominator = (x_p - h) ** 2
        if abs(denominator) < 1e-10:
            return "Error: Point cannot have the same x-coordinate as vertex"

        a = (y_p - k) / denominator

        # Format the equation
        equation = f"y = {a}(x - {h})² + {k}"

        # Expand to standard form if needed
        x = sp.Symbol('x')
        expr = a * (x - h)**2 + k
        expanded = sp.expand(expr)

        result = {
            "vertex_form": equation,
            "standard_form": f"y = {expanded}",
            "parameters": {
                "a": round(a, 4),
                "h": h,
                "k": k
            }
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return f"Error fitting quadratic model: {str(e)}"


@tool
def fit_linear_model(point1_json: str, point2_json: str) -> str:
    """
    Determines the equation of a line y = mx + c given two points.

    Args:
        point1_json: JSON dict of first point. Format: '{"x": 1, "y": 3}'
        point2_json: JSON dict of second point. Format: '{"x": 4, "y": 9}'

    Returns:
        String with the line equation

    Example:
        fit_linear_model('{"x":1,"y":3}', '{"x":4,"y":9}')
    """
    try:
        import json

        p1 = json.loads(point1_json)
        p2 = json.loads(point2_json)

        x1, y1 = p1['x'], p1['y']
        x2, y2 = p2['x'], p2['y']

        # Calculate slope m = (y2 - y1) / (x2 - x1)
        if abs(x2 - x1) < 1e-10:
            return f"Vertical line: x = {x1}"

        m = (y2 - y1) / (x2 - x1)

        # Calculate intercept c using y = mx + c => c = y - mx
        c = y1 - m * x1

        result = {
            "equation": f"y = {m}x + {c}",
            "slope_m": round(m, 4),
            "intercept_c": round(c, 4)
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return f"Error fitting linear model: {str(e)}"


@tool
def evaluate_model(equation: str, x_value: float) -> str:
    """
    Evaluates a mathematical model at a specific x value.

    Args:
        equation: The equation (right side only, e.g., "2*x**2 + 3*x + 1")
        x_value: The x value to evaluate at

    Returns:
        String with the calculated y value

    Example:
        evaluate_model("2*x**2 + 3*x + 1", 5) calculates y when x=5
    """
    try:
        x = sp.Symbol('x')
        expr = sp.sympify(equation)
        result = expr.subs(x, x_value)

        return f"For x = {x_value}, y = {float(result.evalf())}"

    except Exception as e:
        return f"Error evaluating model: {str(e)}"
