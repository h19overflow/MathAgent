"""
Matrix Tools
Purpose: Perform matrix operations and solve matrix equations.
Role: Multiplies matrices and solves systems of linear equations using matrices.
Dependencies: numpy for matrix operations
"""

from langchain.tools import tool
import numpy as np


@tool
def multiply_matrices(matrix_a_json: str, matrix_b_json: str) -> str:
    """
    Performs matrix multiplication A × B.

    Args:
        matrix_a_json: JSON string of matrix A (list of lists).
                      Format: '[[1, 2], [3, 4]]'
        matrix_b_json: JSON string of matrix B (list of lists).
                      Format: '[[5, 6], [7, 8]]'

    Returns:
        String with the resulting matrix

    Example:
        multiply_matrices('[[1,2],[3,4]]', '[[5,6],[7,8]]')
    """
    try:
        import json

        matrix_a = np.array(json.loads(matrix_a_json))
        matrix_b = np.array(json.loads(matrix_b_json))

        # Check if multiplication is possible
        if matrix_a.shape[1] != matrix_b.shape[0]:
            return f"Error: Cannot multiply matrices with shapes {matrix_a.shape} and {matrix_b.shape}"

        result = np.matmul(matrix_a, matrix_b)

        return f"Result:\n{result.tolist()}"

    except Exception as e:
        return f"Error multiplying matrices: {str(e)}"


@tool
def solve_matrix_equation(matrix_a_json: str, matrix_b_json: str) -> str:
    """
    Solves the matrix equation AX = B for X using X = A⁻¹B.

    Useful for solving systems of linear equations.

    Args:
        matrix_a_json: JSON string of coefficient matrix A (must be square and invertible).
                      Format: '[[2, 1], [1, 3]]'
        matrix_b_json: JSON string of constant matrix B.
                      Format: '[[5], [7]]'

    Returns:
        String with the solution matrix X

    Example:
        solve_matrix_equation('[[2,1],[1,3]]', '[[5],[7]]') solves for X
    """
    try:
        import json

        matrix_a = np.array(json.loads(matrix_a_json), dtype=float)
        matrix_b = np.array(json.loads(matrix_b_json), dtype=float)

        # Check if A is square
        if matrix_a.shape[0] != matrix_a.shape[1]:
            return f"Error: Matrix A must be square, got shape {matrix_a.shape}"

        # Check if dimensions are compatible
        if matrix_a.shape[0] != matrix_b.shape[0]:
            return f"Error: Incompatible dimensions A{matrix_a.shape} and B{matrix_b.shape}"

        # Calculate determinant
        det_a = np.linalg.det(matrix_a)
        if abs(det_a) < 1e-10:
            return "Error: Matrix A is singular (determinant ≈ 0), cannot find inverse"

        # Solve using X = A^(-1) * B
        a_inv = np.linalg.inv(matrix_a)
        x = np.matmul(a_inv, matrix_b)

        return f"Solution X:\n{x.tolist()}"

    except Exception as e:
        return f"Error solving matrix equation: {str(e)}"


@tool
def calculate_matrix_determinant(matrix_json: str) -> str:
    """
    Calculates the determinant of a square matrix.

    Args:
        matrix_json: JSON string of square matrix (list of lists).
                    Format: '[[1, 2], [3, 4]]'

    Returns:
        String with the determinant value

    Example:
        calculate_matrix_determinant('[[1,2],[3,4]]')
    """
    try:
        import json

        matrix = np.array(json.loads(matrix_json), dtype=float)

        if matrix.shape[0] != matrix.shape[1]:
            return f"Error: Matrix must be square, got shape {matrix.shape}"

        det = np.linalg.det(matrix)

        return f"Determinant: {det}"

    except Exception as e:
        return f"Error calculating determinant: {str(e)}"


@tool
def calculate_matrix_inverse(matrix_json: str) -> str:
    """
    Calculates the inverse of a square matrix.

    Args:
        matrix_json: JSON string of square invertible matrix.
                    Format: '[[1, 2], [3, 4]]'

    Returns:
        String with the inverse matrix

    Example:
        calculate_matrix_inverse('[[4,7],[2,6]]')
    """
    try:
        import json

        matrix = np.array(json.loads(matrix_json), dtype=float)

        if matrix.shape[0] != matrix.shape[1]:
            return f"Error: Matrix must be square, got shape {matrix.shape}"

        det = np.linalg.det(matrix)
        if abs(det) < 1e-10:
            return "Error: Matrix is singular (determinant ≈ 0), no inverse exists"

        inverse = np.linalg.inv(matrix)

        return f"Inverse:\n{inverse.tolist()}"

    except Exception as e:
        return f"Error calculating inverse: {str(e)}"
