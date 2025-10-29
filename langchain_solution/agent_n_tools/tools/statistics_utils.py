"""
Statistics Utilities Tool
Purpose: Provide statistical analysis tools for frequency distributions, grouped data, and statistical calculations.
Role: Helps agents solve statistics problems with grouped data and perform validation.
"""

from langchain.tools import tool
from typing import List, Dict, Union, Tuple
import numpy as np


@tool
def calculate_grouped_mean(frequencies: List[int], midpoints: List[Union[int, float]]) -> str:
    """Calculate the mean of grouped data.

    Args:
        frequencies: List of frequencies for each class (e.g., [5, 10, 8, 3])
        midpoints: List of class midpoints (e.g., [10, 20, 30, 40])

    Returns:
        String with the calculated mean
    """
    try:
        if len(frequencies) != len(midpoints):
            return "Error: Frequencies and midpoints must have the same length"

        total_frequency = sum(frequencies)
        if total_frequency == 0:
            return "Error: Total frequency cannot be zero"

        weighted_sum = sum(f * m for f, m in zip(frequencies, midpoints))
        mean = weighted_sum / total_frequency

        return f"Grouped Mean: {mean:.2f}"
    except Exception as e:
        return f"Error calculating grouped mean: {str(e)}"


@tool
def calculate_grouped_variance(frequencies: List[int], midpoints: List[Union[int, float]]) -> str:
    """Calculate the variance of grouped data.

    Args:
        frequencies: List of frequencies for each class
        midpoints: List of class midpoints

    Returns:
        String with the calculated variance
    """
    try:
        if len(frequencies) != len(midpoints):
            return "Error: Frequencies and midpoints must have the same length"

        total_frequency = sum(frequencies)
        if total_frequency == 0:
            return "Error: Total frequency cannot be zero"

        # Calculate mean
        mean = sum(f * m for f, m in zip(frequencies, midpoints)) / total_frequency

        # Calculate variance
        variance = sum(f * (m - mean) ** 2 for f, m in zip(frequencies, midpoints)) / total_frequency

        return f"Grouped Variance: {variance:.2f}"
    except Exception as e:
        return f"Error calculating grouped variance: {str(e)}"


@tool
def calculate_grouped_standard_deviation(frequencies: List[int], midpoints: List[Union[int, float]]) -> str:
    """Calculate the standard deviation of grouped data.

    Args:
        frequencies: List of frequencies for each class
        midpoints: List of class midpoints

    Returns:
        String with the calculated standard deviation
    """
    try:
        if len(frequencies) != len(midpoints):
            return "Error: Frequencies and midpoints must have the same length"

        total_frequency = sum(frequencies)
        if total_frequency == 0:
            return "Error: Total frequency cannot be zero"

        # Calculate mean
        mean = sum(f * m for f, m in zip(frequencies, midpoints)) / total_frequency

        # Calculate variance
        variance = sum(f * (m - mean) ** 2 for f, m in zip(frequencies, midpoints)) / total_frequency

        # Standard deviation is square root of variance
        std_dev = np.sqrt(variance)

        return f"Grouped Standard Deviation: {std_dev:.2f}"
    except Exception as e:
        return f"Error calculating grouped standard deviation: {str(e)}"


@tool
def calculate_sum_fx(frequencies: List[int], midpoints: List[Union[int, float]]) -> str:
    """Calculate the sum of (frequency × midpoint) for grouped data.

    This is used in statistics formulas for mean calculation: Σfx / Σf

    Args:
        frequencies: List of frequencies
        midpoints: List of class midpoints

    Returns:
        String with Σfx value
    """
    try:
        if len(frequencies) != len(midpoints):
            return "Error: Frequencies and midpoints must have the same length"

        result = sum(f * m for f, m in zip(frequencies, midpoints))
        return f"Sum of fx (Σfx): {result}"
    except Exception as e:
        return f"Error calculating Σfx: {str(e)}"


@tool
def calculate_sum_fx_squared(frequencies: List[int], midpoints: List[Union[int, float]]) -> str:
    """Calculate the sum of (frequency × midpoint²) for grouped data.

    This is used in statistics formulas: Σfx² - (Σfx)² / Σf

    Args:
        frequencies: List of frequencies
        midpoints: List of class midpoints

    Returns:
        String with Σfx² value
    """
    try:
        if len(frequencies) != len(midpoints):
            return "Error: Frequencies and midpoints must have the same length"

        result = sum(f * (m ** 2) for f, m in zip(frequencies, midpoints))
        return f"Sum of fx² (Σfx²): {result}"
    except Exception as e:
        return f"Error calculating Σfx²: {str(e)}"


@tool
def calculate_cumulative_frequency(frequencies: List[int]) -> str:
    """Calculate cumulative frequency for a frequency distribution.

    Args:
        frequencies: List of frequencies

    Returns:
        String with cumulative frequencies
    """
    try:
        cumulative = []
        total = 0
        for freq in frequencies:
            total += freq
            cumulative.append(total)

        return f"Cumulative Frequencies: {cumulative}"
    except Exception as e:
        return f"Error calculating cumulative frequency: {str(e)}"


@tool
def calculate_relative_frequency(frequencies: List[int]) -> str:
    """Calculate relative frequencies (as decimals and percentages).

    Args:
        frequencies: List of frequencies

    Returns:
        String with relative frequencies
    """
    try:
        total_frequency = sum(frequencies)
        if total_frequency == 0:
            return "Error: Total frequency cannot be zero"

        relative_freq = [f / total_frequency for f in frequencies]
        percentages = [f"{(rf * 100):.2f}%" for rf in relative_freq]

        result_str = "Relative Frequencies: "
        for i, (rf, pct) in enumerate(zip(relative_freq, percentages)):
            result_str += f"f{i+1}={rf:.4f} ({pct}), "

        return result_str.rstrip(", ")
    except Exception as e:
        return f"Error calculating relative frequency: {str(e)}"


@tool
def calculate_median_class(frequencies: List[int], class_boundaries: List[Tuple[Union[int, float], Union[int, float]]]) -> str:
    """Find the median class for grouped data.

    Args:
        frequencies: List of frequencies
        class_boundaries: List of (lower, upper) tuples for each class

    Returns:
        String with median class information
    """
    try:
        total_frequency = sum(frequencies)
        if total_frequency == 0:
            return "Error: Total frequency cannot be zero"

        # Find cumulative frequencies
        cumulative = []
        total = 0
        for freq in frequencies:
            total += freq
            cumulative.append(total)

        # Median position
        median_pos = total_frequency / 2

        # Find median class
        for i, cum_freq in enumerate(cumulative):
            if cum_freq >= median_pos:
                lower, upper = class_boundaries[i]
                return f"Median Class: [{lower}, {upper}) with cumulative frequency up to {cum_freq}"

        return "Error: Could not determine median class"
    except Exception as e:
        return f"Error calculating median class: {str(e)}"
