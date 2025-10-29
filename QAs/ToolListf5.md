 Variation
code
Python
def solve_variation(variation_type: str, known_values: dict, target_variable: str) -> float:
    """Solves direct, inverse, or joint variation problems by finding the constant 'k' and computing the result."""
    # Example: variation_type='direct_square', known_values={'y1': 3.08, 'x1': 2.8, 'y2': 19.25}, target_variable='x2'
    pass
12. Matrices
code
Python
def multiply_matrices(matrix_a: list[list], matrix_b: list[list]) -> list[list]:
    """Performs matrix multiplication."""
    pass

def solve_matrix_equation(matrix_a: list[list], matrix_b: list[list]) -> list[list]:
    """Solves the system of linear equations AX = B for X, using the formula X = A⁻¹B."""
    pass
13. Insurance
code
Python
def calculate_premium(face_value: float, rate_per_1000: float) -> float:
    """Calculates the total insurance premium based on a face value and a given rate per RM1000."""
    pass
14. Taxation
code
Python
def calculate_progressive_tax(value: float, rate_schedule: list[dict]) -> float:
    """Calculates a total amount based on a progressive rate table (e.g., road tax)."""
    # Example rate_schedule: [{'min': 1601, 'max': 1800, 'base': 200.00, 'progressive_rate': 0.40}]
    pass

def calculate_tax_relief(relief_items: dict, relief_limits: dict) -> float:
    """Calculates the total allowable tax relief by applying limits to each item."""
    pass
15. Congruency, Enlargement and Combined Transformations
code
Python
def solve_enlargement(object_area: float, image_area: float = None, scale_factor: float = None) -> dict:
    """Calculates the scale factor 'k' or image/object area using the formula Area_image = k² * Area_object."""
    pass
16. Ratios and Graphs of Trigonometric Functions
code
Python
def solve_right_triangle(side_a: float = None, side_b: float = None, hypotenuse: float = None) -> dict:
    """Calculates all sides and trigonometric ratios (sin, cos, tan) for a right-angled triangle."""
    pass

def solve_trig_equation(equation: str) -> float:
    """Solves basic trigonometric equations like 'sin(x) = 0.5' for a given range."""
    pass
17. Measures of Dispersion for Grouped Data
code
Python
def calculate_grouped_stats(class_intervals: list[dict]) -> dict:
    """Calculates mean, variance, and standard deviation from grouped data (histogram or frequency table)."""
    # Example class_intervals: [{'midpoint': 3.45, 'frequency': 5}, ...]
    pass
18. Mathematical Modeling
code
Python
def fit_quadratic_model(vertex: dict, point: dict) -> str:
    """Determines the equation of a parabola (y = a(x-h)² + k) given its vertex and one other point."""
    pass