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

# ============================================================================
# CATEGORIZED TOOL LISTS FOR DOMAIN-SPECIFIC SOLVERS
# ============================================================================

# Category 1: ALGEBRA & EQUATIONS (13 tools)
# Covers: Quadratic functions, Sequences, Variation, Inequalities
ALGEBRA_EQUATIONS_TOOLS = [
    # Quadratic tools (3)
    analyze_quadratic,
    solve_quadratic_equation,
    find_quadratic_vertex,
    # Sequence tools (2)
    analyze_sequence,
    find_nth_term,
    # Variation tools (1)
    solve_variation,
    # Inequality tools (7)
    plot_linear_inequality,
    validate_point_in_inequality,
    find_inequality_intercepts,
    check_boundary_line,
    validate_inequality_solution_set,
    convert_region_to_inequality,
]

# Category 2: GEOMETRY & SPATIAL (9 tools)
# Covers: Geometry transformations, Trigonometry, Motion graphs
GEOMETRY_SPATIAL_TOOLS = [
    # Geometry tools (3)
    solve_enlargement,
    calculate_scale_factor_from_lengths,
    calculate_area_from_scale,
    # Trigonometry tools (3)
    solve_right_triangle,
    solve_trig_equation,
    calculate_trig_ratio,
    # Motion tools (3)
    calculate_motion_gradient,
    calculate_motion_area,
    analyze_uniform_motion,
]

# Category 3: DISCRETE MATHEMATICS (15 tools)
# Covers: Sets, Graph theory, Probability, Number bases
DISCRETE_MATH_TOOLS = [
    # Set tools (5)
    solve_venn_diagram,
    calculate_set_union,
    calculate_set_intersection,
    calculate_set_difference,
    calculate_set_complement,
    # Graph theory tools (3)
    analyze_graph_properties,
    find_shortest_path,
    calculate_graph_degree,
    # Probability tools (4)
    generate_sample_space,
    calculate_probability,
    count_favorable_outcomes,
    calculate_combined_probability,
    # Base conversion tools (3)
    convert_base,
    validate_number_in_base,
    convert_base_list,
]

# Category 4: STATISTICS (3 tools)
# Covers: Ungrouped data statistics
STATISTICS_TOOLS = [
    calculate_ungrouped_statistics,
    calculate_quartiles,
    calculate_iqr,
]

# Category 5: LINEAR ALGEBRA (4 tools)
# Covers: Matrix operations
LINEAR_ALGEBRA_TOOLS = [
    multiply_matrices,
    solve_matrix_equation,
    calculate_matrix_determinant,
    calculate_matrix_inverse,
]

# Category 6: APPLIED MATHEMATICS (10 tools)
# Covers: Financial management, Insurance & Taxation, Mathematical modeling
APPLIED_MATH_TOOLS = [
    # Financial tools (3)
    analyze_budget,
    calculate_savings_rate,
    check_budget_viability,
    # Insurance and taxation tools (4)
    calculate_premium,
    calculate_progressive_tax,
    calculate_tax_relief,
    calculate_taxable_income,
    # Modeling tools (3)
    fit_quadratic_model,
    fit_linear_model,
    evaluate_model,
]

# Mapping dictionary: category name -> tool list
TOOL_CATEGORIES = {
    "ALGEBRA_EQUATIONS": ALGEBRA_EQUATIONS_TOOLS,
    "GEOMETRY_SPATIAL": GEOMETRY_SPATIAL_TOOLS,
    "DISCRETE_MATH": DISCRETE_MATH_TOOLS,
    "STATISTICS": STATISTICS_TOOLS,
    "LINEAR_ALGEBRA": LINEAR_ALGEBRA_TOOLS,
    "APPLIED_MATH": APPLIED_MATH_TOOLS,
    "GENERAL": None,  # Will use MATH_TOOLS for general category
}

# ============================================================================
# COMPLETE TOOL LIST (All 54 tools)
# ============================================================================

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
    # Category lists
    "ALGEBRA_EQUATIONS_TOOLS",
    "GEOMETRY_SPATIAL_TOOLS",
    "DISCRETE_MATH_TOOLS",
    "STATISTICS_TOOLS",
    "LINEAR_ALGEBRA_TOOLS",
    "APPLIED_MATH_TOOLS",
    "TOOL_CATEGORIES",
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
