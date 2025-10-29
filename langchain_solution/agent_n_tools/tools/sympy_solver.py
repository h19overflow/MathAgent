"""
SymPy Solver Tool
Purpose: Provide symbolic math operations for solving equations, simplifying expressions,
         and validating mathematical relationships.
Role: Enables agents to verify calculations and solve algebraic problems symbolically.
"""

from langchain.tools import tool
from typing import Union
import sympy as sp


@tool
def solve_equation(equation: str, variable: str = "x") -> str:
    """Solve an algebraic equation symbolically.

    Args:
        equation: The equation to solve (e.g., "x**2 - 4 = 0" or "2*x + 5 = 15")
        variable: The variable to solve for (default: "x")

    Returns:
        String representation of the solution(s)

    Raises:
        ValueError: If equation cannot be parsed or solved
    """
    try:
        var = sp.Symbol(variable)
        # Parse the equation
        eq = sp.sympify(equation)
        solutions = sp.solve(eq, var)
        return f"Solutions for {variable}: {solutions}"
    except Exception as e:
        return f"Error solving equation: {str(e)}"


@tool
def simplify_expression(expression: str) -> str:
    """Simplify a mathematical expression.

    Args:
        expression: The expression to simplify (e.g., "2*x + 3*x - 5")

    Returns:
        String representation of the simplified expression

    Raises:
        ValueError: If expression cannot be parsed
    """
    try:
        expr = sp.sympify(expression)
        simplified = sp.simplify(expr)
        return f"Simplified: {simplified}"
    except Exception as e:
        return f"Error simplifying expression: {str(e)}"


@tool
def expand_expression(expression: str) -> str:
    """Expand a mathematical expression (e.g., factored to polynomial form).

    Args:
        expression: The expression to expand (e.g., "(x + 1)*(x - 1)")

    Returns:
        String representation of the expanded expression

    Raises:
        ValueError: If expression cannot be parsed
    """
    try:
        expr = sp.sympify(expression)
        expanded = sp.expand(expr)
        return f"Expanded: {expanded}"
    except Exception as e:
        return f"Error expanding expression: {str(e)}"


@tool
def check_inequality(inequality: str, variable: str = "x") -> str:
    """Check and validate an inequality symbolically.

    Args:
        inequality: The inequality to check (e.g., "x + 5 > 10" or "2*x <= 8")
        variable: The variable in the inequality (default: "x")

    Returns:
        String representation of the solution set for the inequality

    Raises:
        ValueError: If inequality cannot be parsed
    """
    try:
        var = sp.Symbol(variable)
        # Parse the inequality
        ineq = sp.sympify(inequality)
        solutions = sp.solve(ineq, var)
        return f"Inequality {inequality} solution: {solutions}"
    except Exception as e:
        return f"Error checking inequality: {str(e)}"


@tool
def factor_expression(expression: str) -> str:
    """Factor a mathematical expression.

    Args:
        expression: The expression to factor (e.g., "x**2 - 5*x + 6")

    Returns:
        String representation of the factored expression

    Raises:
        ValueError: If expression cannot be parsed or factored
    """
    try:
        expr = sp.sympify(expression)
        factored = sp.factor(expr)
        return f"Factored: {factored}"
    except Exception as e:
        return f"Error factoring expression: {str(e)}"
