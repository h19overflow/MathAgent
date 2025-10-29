"""
Motion Graph Tools
Purpose: Analyze speed-time and distance-time graphs.
Role: Calculates gradients (acceleration/speed) and areas (distance) from motion graphs.
Dependencies: None (uses basic calculus concepts)
"""

from langchain.tools import tool


@tool
def calculate_motion_gradient(points_json: str, time_start: float, time_end: float) -> str:
    """
    Calculates the gradient (rate of change) of a motion graph over a time interval.

    For speed-time graphs: gradient = acceleration
    For distance-time graphs: gradient = speed

    Args:
        points_json: JSON string list of coordinate pairs [time, value].
                    Format: '[[0, 0], [40, 15], [120, 15], [150, 0]]'
        time_start: Start time of the interval
        time_end: End time of the interval

    Returns:
        String with the calculated gradient

    Example:
        calculate_motion_gradient('[[0,0],[40,15]]', 0, 40) calculates acceleration
    """
    try:
        import json

        points = json.loads(points_json)

        # Find the two points at the interval boundaries
        point_start = None
        point_end = None

        for point in points:
            t, v = point[0], point[1]
            if abs(t - time_start) < 1e-9:
                point_start = (t, v)
            if abs(t - time_end) < 1e-9:
                point_end = (t, v)

        if point_start is None or point_end is None:
            return f"Error: Could not find points at t={time_start} and t={time_end}"

        # Calculate gradient: (v2 - v1) / (t2 - t1)
        delta_t = point_end[0] - point_start[0]
        delta_v = point_end[1] - point_start[1]

        if abs(delta_t) < 1e-9:
            return "Error: Time interval cannot be zero"

        gradient = delta_v / delta_t

        return f"Gradient from t={time_start} to t={time_end}: {gradient}"

    except Exception as e:
        return f"Error calculating gradient: {str(e)}"


@tool
def calculate_motion_area(points_json: str, time_start: float, time_end: float) -> str:
    """
    Calculates the area under a motion graph over a time interval.

    For speed-time graphs: area = distance travelled
    For acceleration-time graphs: area = change in speed

    Uses trapezoidal rule for irregular shapes.

    Args:
        points_json: JSON string list of coordinate pairs [time, value].
                    Format: '[[0, 0], [40, 15], [120, 15], [150, 0]]'
        time_start: Start time of the interval
        time_end: End time of the interval

    Returns:
        String with the calculated area

    Example:
        calculate_motion_area('[[40,15],[120,15]]', 40, 120) calculates distance
    """
    try:
        import json

        points = json.loads(points_json)
        points = sorted(points, key=lambda p: p[0])  # Sort by time

        # Filter points within the interval
        relevant_points = [p for p in points if time_start <= p[0] <= time_end]

        # Add boundary points if needed
        if len(relevant_points) == 0:
            return "Error: No points found in the specified interval"

        if relevant_points[0][0] > time_start:
            # Interpolate value at time_start
            for i in range(len(points) - 1):
                if points[i][0] <= time_start <= points[i+1][0]:
                    t1, v1 = points[i]
                    t2, v2 = points[i+1]
                    v_start = v1 + (v2 - v1) * (time_start - t1) / (t2 - t1)
                    relevant_points.insert(0, [time_start, v_start])
                    break

        if relevant_points[-1][0] < time_end:
            # Interpolate value at time_end
            for i in range(len(points) - 1):
                if points[i][0] <= time_end <= points[i+1][0]:
                    t1, v1 = points[i]
                    t2, v2 = points[i+1]
                    v_end = v1 + (v2 - v1) * (time_end - t1) / (t2 - t1)
                    relevant_points.append([time_end, v_end])
                    break

        # Calculate area using trapezoidal rule
        area = 0
        for i in range(len(relevant_points) - 1):
            t1, v1 = relevant_points[i]
            t2, v2 = relevant_points[i+1]
            area += (t2 - t1) * (v1 + v2) / 2

        return f"Area from t={time_start} to t={time_end}: {area}"

    except Exception as e:
        return f"Error calculating area: {str(e)}"


@tool
def analyze_uniform_motion(speed: float, time: float) -> str:
    """
    Calculates distance for uniform (constant speed) motion.

    Args:
        speed: Constant speed (e.g., in m/s or km/h)
        time: Time duration

    Returns:
        String with the calculated distance

    Example:
        analyze_uniform_motion(15, 80) calculates distance at 15 m/s for 80 seconds
    """
    try:
        distance = speed * time
        return f"Distance = speed × time = {speed} × {time} = {distance}"

    except Exception as e:
        return f"Error calculating distance: {str(e)}"
