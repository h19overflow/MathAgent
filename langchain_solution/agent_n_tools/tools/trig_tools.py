"""
Trigonometry Tools
Purpose: Solve right triangle problems and trigonometric equations.
Role: Calculates sides, angles, and trigonometric ratios for right triangles.
Dependencies: math for trigonometric functions
"""

from langchain.tools import tool
import math


@tool
def solve_right_triangle(side_a: float = None, side_b: float = None,
                        hypotenuse: float = None) -> str:
    """
    Calculates all sides and trigonometric ratios for a right-angled triangle.

    Provide any two sides to calculate the third and all trig ratios.

    Args:
        side_a: Length of one perpendicular side (optional)
        side_b: Length of other perpendicular side (optional)
        hypotenuse: Length of hypotenuse (optional)

    Returns:
        String with JSON-formatted triangle analysis

    Example:
        solve_right_triangle(side_a=3, side_b=4) calculates hypotenuse and ratios
        solve_right_triangle(side_a=3, hypotenuse=5) calculates side_b
    """
    try:
        import json

        # Count provided sides
        provided = sum(x is not None for x in [side_a, side_b, hypotenuse])

        if provided < 2:
            return "Error: Provide at least 2 sides"

        # Calculate missing side using Pythagorean theorem
        if side_a is not None and side_b is not None:
            # Calculate hypotenuse: c² = a² + b²
            hypotenuse = math.sqrt(side_a**2 + side_b**2)

        elif side_a is not None and hypotenuse is not None:
            # Calculate side_b: b² = c² - a²
            if hypotenuse <= side_a:
                return "Error: Hypotenuse must be longer than side_a"
            side_b = math.sqrt(hypotenuse**2 - side_a**2)

        elif side_b is not None and hypotenuse is not None:
            # Calculate side_a: a² = c² - b²
            if hypotenuse <= side_b:
                return "Error: Hypotenuse must be longer than side_b"
            side_a = math.sqrt(hypotenuse**2 - side_b**2)

        # Calculate angles (in degrees)
        # Angle A (opposite to side_a)
        angle_a_rad = math.asin(side_a / hypotenuse)
        angle_a_deg = math.degrees(angle_a_rad)

        # Angle B (opposite to side_b)
        angle_b_deg = 90 - angle_a_deg

        # Calculate trig ratios for angle A
        sin_a = side_a / hypotenuse
        cos_a = side_b / hypotenuse
        tan_a = side_a / side_b if side_b != 0 else float('inf')

        result = {
            "sides": {
                "side_a": round(side_a, 4),
                "side_b": round(side_b, 4),
                "hypotenuse": round(hypotenuse, 4)
            },
            "angles": {
                "angle_A_degrees": round(angle_a_deg, 4),
                "angle_B_degrees": round(angle_b_deg, 4),
                "right_angle": 90
            },
            "trig_ratios_for_angle_A": {
                "sin": round(sin_a, 4),
                "cos": round(cos_a, 4),
                "tan": round(tan_a, 4)
            }
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return f"Error solving right triangle: {str(e)}"


@tool
def solve_trig_equation(equation: str, angle_min: float = 0, angle_max: float = 360) -> str:
    """
    Solves basic trigonometric equations like sin(x) = value for a range.

    Args:
        equation: Equation in form "sin(x) = 0.5" or "cos(x) = 0.866"
        angle_min: Minimum angle in degrees (default: 0)
        angle_max: Maximum angle in degrees (default: 360)

    Returns:
        String with solutions in the specified range

    Example:
        solve_trig_equation("sin(x) = 0.5", 0, 360) finds x where sin(x) = 0.5
    """
    try:
        # Parse the equation
        parts = equation.replace(" ", "").split("=")
        if len(parts) != 2:
            return "Error: Equation must be in form 'sin(x) = value'"

        left = parts[0].lower()
        value = float(parts[1])

        # Determine the trig function
        if 'sin' in left:
            trig_func = 'sin'
        elif 'cos' in left:
            trig_func = 'cos'
        elif 'tan' in left:
            trig_func = 'tan'
        else:
            return "Error: Equation must use sin, cos, or tan"

        # Validate value range
        if trig_func in ['sin', 'cos'] and abs(value) > 1:
            return f"Error: {trig_func} value must be between -1 and 1"

        solutions = []

        if trig_func == 'sin':
            # Principal solution
            principal = math.degrees(math.asin(value))
            solutions.append(principal % 360)

            # Second solution in [0, 360)
            second = (180 - principal) % 360
            if second != solutions[0]:
                solutions.append(second)

        elif trig_func == 'cos':
            principal = math.degrees(math.acos(value))
            solutions.append(principal % 360)

            # Second solution
            second = (360 - principal) % 360
            if second != solutions[0]:
                solutions.append(second)

        elif trig_func == 'tan':
            principal = math.degrees(math.atan(value))
            solutions.append(principal % 360)

            # Tangent has period 180°
            second = (principal + 180) % 360
            if second != solutions[0]:
                solutions.append(second)

        # Filter solutions in range
        solutions = [s for s in solutions if angle_min <= s <= angle_max]
        solutions = sorted(set([round(s, 4) for s in solutions]))

        return f"Solutions for {equation} in [{angle_min}°, {angle_max}°]: {solutions}"

    except Exception as e:
        return f"Error solving equation: {str(e)}"


@tool
def calculate_trig_ratio(angle_degrees: float, ratio_type: str) -> str:
    """
    Calculates a trigonometric ratio for a given angle.

    Args:
        angle_degrees: Angle in degrees
        ratio_type: Type of ratio - "sin", "cos", or "tan"

    Returns:
        String with the calculated ratio

    Example:
        calculate_trig_ratio(30, "sin") returns 0.5
    """
    try:
        angle_rad = math.radians(angle_degrees)

        if ratio_type.lower() == "sin":
            result = math.sin(angle_rad)
        elif ratio_type.lower() == "cos":
            result = math.cos(angle_rad)
        elif ratio_type.lower() == "tan":
            result = math.tan(angle_rad)
        else:
            return "Error: ratio_type must be 'sin', 'cos', or 'tan'"

        return f"{ratio_type}({angle_degrees}°) = {round(result, 6)}"

    except Exception as e:
        return f"Error calculating ratio: {str(e)}"
