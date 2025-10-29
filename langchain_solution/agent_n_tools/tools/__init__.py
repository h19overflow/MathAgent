"""
Math Tools Package
Exports all math tools for use with LangChain agents.
"""

from .sympy_solver import (
    solve_equation,
    simplify_expression,
    expand_expression,
    check_inequality,
    factor_expression,
)

from .numpy_calculator import (
    calculate_sum,
    calculate_mean,
    calculate_variance,
    calculate_standard_deviation,
    calculate_percentage,
    calculate_sum_of_squares,
    calculate_frequency_distribution,
    validate_sum,
)

from .inequality_grapher import (
    plot_linear_inequality,
    validate_point_in_inequality,
    find_inequality_intercepts,
    check_boundary_line,
    validate_inequality_solution_set,
)

from .statistics_utils import (
    calculate_grouped_mean,
    calculate_grouped_variance,
    calculate_grouped_standard_deviation,
    calculate_sum_fx,
    calculate_sum_fx_squared,
    calculate_cumulative_frequency,
    calculate_relative_frequency,
    calculate_median_class,
)

# Collect all tools for easy access
MATH_TOOLS = [
    # SymPy tools
    solve_equation,
    simplify_expression,
    expand_expression,
    check_inequality,
    factor_expression,
    # NumPy tools
    calculate_sum,
    calculate_mean,
    calculate_variance,
    calculate_standard_deviation,
    calculate_percentage,
    calculate_sum_of_squares,
    calculate_frequency_distribution,
    validate_sum,
    # Inequality tools
    plot_linear_inequality,
    validate_point_in_inequality,
    find_inequality_intercepts,
    check_boundary_line,
    validate_inequality_solution_set,
    # Statistics tools
    calculate_grouped_mean,
    calculate_grouped_variance,
    calculate_grouped_standard_deviation,
    calculate_sum_fx,
    calculate_sum_fx_squared,
    calculate_cumulative_frequency,
    calculate_relative_frequency,
    calculate_median_class,
]

__all__ = [
    "MATH_TOOLS",
    # SymPy exports
    "solve_equation",
    "simplify_expression",
    "expand_expression",
    "check_inequality",
    "factor_expression",
    # NumPy exports
    "calculate_sum",
    "calculate_mean",
    "calculate_variance",
    "calculate_standard_deviation",
    "calculate_percentage",
    "calculate_sum_of_squares",
    "calculate_frequency_distribution",
    "validate_sum",
    # Inequality exports
    "plot_linear_inequality",
    "validate_point_in_inequality",
    "find_inequality_intercepts",
    "check_boundary_line",
    "validate_inequality_solution_set",
    # Statistics exports
    "calculate_grouped_mean",
    "calculate_grouped_variance",
    "calculate_grouped_standard_deviation",
    "calculate_sum_fx",
    "calculate_sum_fx_squared",
    "calculate_cumulative_frequency",
    "calculate_relative_frequency",
    "calculate_median_class",
]
