"""
NumPy Calculator Tool
Purpose: Provide numerical calculations for statistics, arrays, and basic math operations.
Role: Enables agents to verify calculations with actual numerical values.
"""

from langchain.tools import tool
from typing import List, Union
import numpy as np


@tool
def calculate_sum(numbers: List[Union[int, float]]) -> str:
    """Calculate the sum of a list of numbers.

    Args:
        numbers: List of numbers to sum (e.g., [1, 2, 3, 4, 5])

    Returns:
        String with the sum result
    """
    try:
        result = np.sum(numbers)
        return f"Sum of {numbers}: {result}"
    except Exception as e:
        return f"Error calculating sum: {str(e)}"


@tool
def calculate_mean(numbers: List[Union[int, float]]) -> str:
    """Calculate the mean (average) of a list of numbers.

    Args:
        numbers: List of numbers to average

    Returns:
        String with the mean result
    """
    try:
        result = np.mean(numbers)
        return f"Mean of {numbers}: {result}"
    except Exception as e:
        return f"Error calculating mean: {str(e)}"


@tool
def calculate_variance(numbers: List[Union[int, float]]) -> str:
    """Calculate the variance of a list of numbers.

    Args:
        numbers: List of numbers to analyze

    Returns:
        String with the variance result
    """
    try:
        result = np.var(numbers)
        return f"Variance of {numbers}: {result}"
    except Exception as e:
        return f"Error calculating variance: {str(e)}"


@tool
def calculate_standard_deviation(numbers: List[Union[int, float]]) -> str:
    """Calculate the standard deviation of a list of numbers.

    Args:
        numbers: List of numbers to analyze

    Returns:
        String with the standard deviation result
    """
    try:
        result = np.std(numbers)
        return f"Standard Deviation of {numbers}: {result}"
    except Exception as e:
        return f"Error calculating standard deviation: {str(e)}"


@tool
def calculate_percentage(value: Union[int, float], total: Union[int, float]) -> str:
    """Calculate the percentage of a value relative to a total.

    Args:
        value: The value to calculate percentage for
        total: The total amount

    Returns:
        String with the percentage result
    """
    try:
        if total == 0:
            return "Error: Total cannot be zero"
        result = (value / total) * 100
        return f"Percentage: {value}/{total} = {result:.2f}%"
    except Exception as e:
        return f"Error calculating percentage: {str(e)}"


@tool
def calculate_sum_of_squares(numbers: List[Union[int, float]]) -> str:
    """Calculate the sum of squares of a list of numbers.

    Args:
        numbers: List of numbers

    Returns:
        String with the sum of squares result
    """
    try:
        result = np.sum(np.array(numbers) ** 2)
        return f"Sum of squares of {numbers}: {result}"
    except Exception as e:
        return f"Error calculating sum of squares: {str(e)}"


@tool
def calculate_frequency_distribution(numbers: List[Union[int, float]]) -> str:
    """Calculate the frequency distribution of a list of numbers.

    Args:
        numbers: List of numbers to analyze

    Returns:
        String with frequency distribution (unique values and their counts)
    """
    try:
        unique, counts = np.unique(numbers, return_counts=True)
        freq_dict = dict(zip(unique, counts))
        return f"Frequency distribution: {freq_dict}"
    except Exception as e:
        return f"Error calculating frequency distribution: {str(e)}"


@tool
def validate_sum(numbers: List[Union[int, float]], expected_sum: Union[int, float]) -> str:
    """Validate if the sum of numbers equals an expected value.

    Args:
        numbers: List of numbers to sum
        expected_sum: The expected sum to validate against

    Returns:
        String indicating if the sum is correct or showing the actual sum
    """
    try:
        actual_sum = np.sum(numbers)
        if abs(actual_sum - expected_sum) < 1e-9:  # Allow for floating point errors
            return f"✓ Sum is correct: {actual_sum}"
        else:
            return f"✗ Sum mismatch. Expected: {expected_sum}, Got: {actual_sum}"
    except Exception as e:
        return f"Error validating sum: {str(e)}"
