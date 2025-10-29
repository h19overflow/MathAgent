"""
Math Tools Package
Exports all math tools for use with LangChain agents.
Organized by mathematical domain for SPM-level problems.
"""


# Inequality and Graphing Tools
from .inequality_grapher import (
    plot_linear_inequality,
    validate_point_in_inequality,
    find_inequality_intercepts,
    check_boundary_line,
    validate_inequality_solution_set,
    convert_region_to_inequality,
)

# Statistics Tools (Grouped Data)


# Quadratic Functions Tools
from .quadratic_tools import (
    analyze_quadratic,
    solve_quadratic_equation,
    find_quadratic_vertex,
)

# Number Base Conversion Tools
from .base_tools import (
    convert_base,
    validate_number_in_base,
    convert_base_list,
)

# Sequence Analysis Tools
from .sequence_tools import (
    analyze_sequence,
    find_nth_term,
)

# Set Operations and Venn Diagram Tools
from .set_tools import (
    solve_venn_diagram,
    calculate_set_union,
    calculate_set_intersection,
    calculate_set_difference,
    calculate_set_complement,
)

# Graph Theory Tools
from .graph_tools import (
    analyze_graph_properties,
    find_shortest_path,
    calculate_graph_degree,
)

# Motion Graph Tools
from .motion_tools import (
    calculate_motion_gradient,
    calculate_motion_area,
    analyze_uniform_motion,
)

# Ungrouped Statistics Tools
from .ungrouped_stats_tools import (
    calculate_ungrouped_statistics,
    calculate_quartiles,
    calculate_iqr,
)

# Probability Tools
from .probability_tools import (
    generate_sample_space,
    calculate_probability,
    count_favorable_outcomes,
    calculate_combined_probability,
)

# Financial Management Tools
from .financial_tools import (
    analyze_budget,
    calculate_savings_rate,
    check_budget_viability,
)

# Variation Tools
from .variation_tools import (
    solve_variation,
)

# Matrix Operations Tools
from .matrix_tools import (
    multiply_matrices,
    solve_matrix_equation,
    calculate_matrix_determinant,
    calculate_matrix_inverse,
)

# Insurance and Taxation Tools
from .insurance_taxation_tools import (
    calculate_premium,
    calculate_progressive_tax,
    calculate_tax_relief,
    calculate_taxable_income,
)

# Geometry and Transformation Tools
from .geometry_tools import (
    solve_enlargement,
    calculate_scale_factor_from_lengths,
    calculate_area_from_scale,
)

# Trigonometry Tools
from .trig_tools import (
    solve_right_triangle,
    solve_trig_equation,
    calculate_trig_ratio,
)

# Mathematical Modeling Tools
from .modeling_tools import (
    fit_quadratic_model,
    fit_linear_model,
    evaluate_model,
)

# Collect all tools for easy access by agents
MATH_TOOLS = [
    # SymPy tools
    # Inequality tools
    plot_linear_inequality,
    validate_point_in_inequality,
    find_inequality_intercepts,
    check_boundary_line,
    validate_inequality_solution_set,
    convert_region_to_inequality,
    # Statistics tools (grouped)
    # Quadratic tools
    analyze_quadratic,
    solve_quadratic_equation,
    find_quadratic_vertex,
    # Base conversion tools
    convert_base,
    validate_number_in_base,
    convert_base_list,
    # Sequence tools
    analyze_sequence,
    find_nth_term,
    # Set tools
    solve_venn_diagram,
    calculate_set_union,
    calculate_set_intersection,
    calculate_set_difference,
    calculate_set_complement,
    # Graph theory tools
    analyze_graph_properties,
    find_shortest_path,
    calculate_graph_degree,
    # Motion tools
    calculate_motion_gradient,
    calculate_motion_area,
    analyze_uniform_motion,
    # Ungrouped statistics tools
    calculate_ungrouped_statistics,
    calculate_quartiles,
    calculate_iqr,
    # Probability tools
    generate_sample_space,
    calculate_probability,
    count_favorable_outcomes,
    calculate_combined_probability,
    # Financial tools
    analyze_budget,
    calculate_savings_rate,
    check_budget_viability,
    # Variation tools
    solve_variation,
    # Matrix tools
    multiply_matrices,
    solve_matrix_equation,
    calculate_matrix_determinant,
    calculate_matrix_inverse,
    # Insurance and taxation tools
    calculate_premium,
    calculate_progressive_tax,
    calculate_tax_relief,
    calculate_taxable_income,
    # Geometry tools
    solve_enlargement,
    calculate_scale_factor_from_lengths,
    calculate_area_from_scale,
    # Trigonometry tools
    solve_right_triangle,
    solve_trig_equation,
    calculate_trig_ratio,
    # Modeling tools
    fit_quadratic_model,
    fit_linear_model,
    evaluate_model,
]

__all__ = [
    "MATH_TOOLS",
    # SymPy exports
    # NumPy exports
    # Inequality exports
    "plot_linear_inequality",
    "validate_point_in_inequality",
    "find_inequality_intercepts",
    "check_boundary_line",
    "validate_inequality_solution_set",
    "convert_region_to_inequality",
    # Statistics exports
    # Quadratic exports
    "analyze_quadratic",
    "solve_quadratic_equation",
    "find_quadratic_vertex",
    # Base conversion exports
    "convert_base",
    "validate_number_in_base",
    "convert_base_list",
    # Sequence exports
    "analyze_sequence",
    "find_nth_term",
    # Set exports
    "solve_venn_diagram",
    "calculate_set_union",
    "calculate_set_intersection",
    "calculate_set_difference",
    "calculate_set_complement",
    # Graph theory exports
    "analyze_graph_properties",
    "find_shortest_path",
    "calculate_graph_degree",
    # Motion exports
    "calculate_motion_gradient",
    "calculate_motion_area",
    "analyze_uniform_motion",
    # Ungrouped statistics exports
    "calculate_ungrouped_statistics",
    "calculate_quartiles",
    "calculate_iqr",
    # Probability exports
    "generate_sample_space",
    "calculate_probability",
    "count_favorable_outcomes",
    "calculate_combined_probability",
    # Financial exports
    "analyze_budget",
    "calculate_savings_rate",
    "check_budget_viability",
    # Variation exports
    "solve_variation",
    # Matrix exports
    "multiply_matrices",
    "solve_matrix_equation",
    "calculate_matrix_determinant",
    "calculate_matrix_inverse",
    # Insurance and taxation exports
    "calculate_premium",
    "calculate_progressive_tax",
    "calculate_tax_relief",
    "calculate_taxable_income",
    # Geometry exports
    "solve_enlargement",
    "calculate_scale_factor_from_lengths",
    "calculate_area_from_scale",
    # Trigonometry exports
    "solve_right_triangle",
    "solve_trig_equation",
    "calculate_trig_ratio",
    # Modeling exports
    "fit_quadratic_model",
    "fit_linear_model",
    "evaluate_model",
]
