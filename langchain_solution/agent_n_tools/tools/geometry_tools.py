"""
Geometry and Transformation Tools
Purpose: Solve problems involving enlargement and area scaling.
Role: Calculates scale factors and transformed areas for geometric enlargements.
Dependencies: None (uses basic geometric formulas)
"""

from langchain.tools import tool


@tool
def solve_enlargement(object_area: float, image_area: float = None,
                     scale_factor: float = None) -> str:
    """
    Calculates scale factor or image/object area using Area_image = k² × Area_object.

    Provide either (object_area and scale_factor) OR (object_area and image_area).

    Args:
        object_area: Area of the original object
        image_area: Area of the enlarged/reduced image (optional)
        scale_factor: Scale factor k (optional)

    Returns:
        String with JSON-formatted result containing calculated values

    Example:
        solve_enlargement(10, scale_factor=2) calculates image area
        solve_enlargement(10, image_area=40) calculates scale factor
    """
    try:
        import json

        if scale_factor is not None:
            # Calculate image area from scale factor
            calculated_image_area = (scale_factor ** 2) * object_area

            result = {
                "object_area": object_area,
                "scale_factor_k": scale_factor,
                "image_area": calculated_image_area,
                "formula": f"Area_image = k² × Area_object = {scale_factor}² × {object_area}"
            }

        elif image_area is not None:
            # Calculate scale factor from areas
            k_squared = image_area / object_area
            calculated_scale_factor = k_squared ** 0.5

            result = {
                "object_area": object_area,
                "image_area": image_area,
                "scale_factor_k": calculated_scale_factor,
                "formula": f"k² = Area_image / Area_object = {image_area} / {object_area}"
            }

        else:
            return "Error: Must provide either image_area or scale_factor"

        return json.dumps(result, indent=2)

    except Exception as e:
        return f"Error solving enlargement: {str(e)}"


@tool
def calculate_scale_factor_from_lengths(object_length: float, image_length: float) -> str:
    """
    Calculates the linear scale factor from corresponding lengths.

    Args:
        object_length: Length of a side in the original object
        image_length: Corresponding length in the image

    Returns:
        String with the scale factor k

    Example:
        calculate_scale_factor_from_lengths(5, 15) returns k = 3
    """
    try:
        if object_length == 0:
            return "Error: Object length cannot be zero"

        scale_factor = image_length / object_length

        return f"Scale factor k = Image length / Object length = {image_length} / {object_length} = {scale_factor}"

    except Exception as e:
        return f"Error calculating scale factor: {str(e)}"


@tool
def calculate_area_from_scale(original_area: float, scale_factor: float) -> str:
    """
    Calculates the new area after applying a scale factor.

    Args:
        original_area: Original area
        scale_factor: Linear scale factor k

    Returns:
        String with the new area

    Example:
        calculate_area_from_scale(20, 3) returns 180 (area scaled by 3² = 9)
    """
    try:
        new_area = original_area * (scale_factor ** 2)

        return f"New area = Original area × k² = {original_area} × {scale_factor}² = {new_area}"

    except Exception as e:
        return f"Error calculating area: {str(e)}"
