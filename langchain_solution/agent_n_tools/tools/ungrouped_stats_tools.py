"""
Ungrouped Statistics Tools
Purpose: Calculate statistics for raw data and frequency tables.
Role: Computes range, quartiles, IQR, variance, and standard deviation.
Dependencies: numpy for numerical operations
"""

from langchain.tools import tool
import numpy as np


@tool
def calculate_ungrouped_statistics(data_json: str, data_type: str = "raw") -> str:
    """
    Calculates comprehensive statistics for ungrouped data.

    Returns mean, range, quartiles, IQR, variance, and standard deviation.

    Args:
        data_json: JSON string of data.
                  For raw data: '[48, 53, 65, 69, 70]'
                  For frequency table: '{"1": 2, "2": 5, "3": 6, "4": 9}'
        data_type: "raw" for list of values, "frequency" for frequency table

    Returns:
        String with JSON-formatted statistics

    Example:
        calculate_ungrouped_statistics('[48, 53, 65, 69, 70]', 'raw')
    """
    try:
        import json

        if data_type == "raw":
            data = json.loads(data_json)
            values = np.array([float(x) for x in data])

        elif data_type == "frequency":
            freq_dict = json.loads(data_json)
            # Expand frequency table to raw data
            values = []
            for value, freq in freq_dict.items():
                values.extend([float(value)] * int(freq))
            values = np.array(values)

        else:
            return "Error: data_type must be 'raw' or 'frequency'"

        # Calculate statistics
        count = len(values)
        mean = np.mean(values)
        range_val = np.max(values) - np.min(values)

        # Quartiles
        q1 = np.percentile(values, 25)
        median = np.percentile(values, 50)
        q3 = np.percentile(values, 75)
        iqr = q3 - q1

        # Variance and standard deviation
        variance = np.var(values, ddof=0)  # Population variance
        std_dev = np.std(values, ddof=0)

        result = {
            "count": count,
            "mean": round(float(mean), 4),
            "range": round(float(range_val), 4),
            "q1": round(float(q1), 4),
            "median_q2": round(float(median), 4),
            "q3": round(float(q3), 4),
            "interquartile_range": round(float(iqr), 4),
            "variance": round(float(variance), 4),
            "standard_deviation": round(float(std_dev), 4)
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return f"Error calculating statistics: {str(e)}"


@tool
def calculate_quartiles(data_json: str) -> str:
    """
    Calculates Q1, Q2 (median), and Q3 for a dataset.

    Args:
        data_json: JSON string list of numbers (e.g., '[1, 2, 3, 4, 5, 6, 7]')

    Returns:
        String with quartile values

    Example:
        calculate_quartiles('[48, 53, 65, 69, 70]')
    """
    try:
        import json

        data = json.loads(data_json)
        values = np.array([float(x) for x in data])

        q1 = np.percentile(values, 25)
        q2 = np.percentile(values, 50)
        q3 = np.percentile(values, 75)

        return f"Q1 = {q1}, Q2 (Median) = {q2}, Q3 = {q3}"

    except Exception as e:
        return f"Error calculating quartiles: {str(e)}"


@tool
def calculate_iqr(data_json: str) -> str:
    """
    Calculates the Interquartile Range (IQR = Q3 - Q1).

    Args:
        data_json: JSON string list of numbers

    Returns:
        String with IQR value

    Example:
        calculate_iqr('[1, 2, 3, 4, 5, 6, 7, 8, 9]')
    """
    try:
        import json

        data = json.loads(data_json)
        values = np.array([float(x) for x in data])

        q1 = np.percentile(values, 25)
        q3 = np.percentile(values, 75)
        iqr = q3 - q1

        return f"IQR = Q3 - Q1 = {q3} - {q1} = {iqr}"

    except Exception as e:
        return f"Error calculating IQR: {str(e)}"
