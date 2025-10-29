"""
Insurance and Taxation Tools
Purpose: Calculate insurance premiums and progressive tax amounts.
Role: Handles insurance premium calculations and tax relief computations.
Dependencies: None (uses basic arithmetic)
"""

from langchain.tools import tool


@tool
def calculate_premium(face_value: float, rate_per_1000: float) -> str:
    """
    Calculates total insurance premium based on face value and rate per RM1000.

    Args:
        face_value: Face value of the insurance policy (e.g., 100000)
        rate_per_1000: Premium rate per RM1000 of coverage (e.g., 2.50)

    Returns:
        String with the calculated premium

    Example:
        calculate_premium(100000, 2.50) calculates premium for RM100,000 coverage
    """
    try:
        premium = (face_value / 1000) * rate_per_1000

        return f"Premium = (Face Value / 1000) × Rate = ({face_value} / 1000) × {rate_per_1000} = {premium}"

    except Exception as e:
        return f"Error calculating premium: {str(e)}"


@tool
def calculate_progressive_tax(value: float, rate_schedule_json: str) -> str:
    """
    Calculates total amount using a progressive rate table (e.g., road tax).

    Args:
        value: The value to calculate tax for (e.g., engine capacity in cc)
        rate_schedule_json: JSON string list of tax brackets.
                           Format: '[{"min": 1601, "max": 1800, "base": 200, "progressive_rate": 0.40}, ...]'

    Returns:
        String with the calculated tax amount

    Example:
        calculate_progressive_tax(1650, '[{"min":1601,"max":1800,"base":200,"progressive_rate":0.40}]')
    """
    try:
        import json

        schedule = json.loads(rate_schedule_json)

        # Find the applicable bracket
        for bracket in schedule:
            if bracket['min'] <= value <= bracket['max']:
                base = bracket['base']
                progressive_rate = bracket['progressive_rate']
                excess = value - bracket['min']
                tax = base + (excess * progressive_rate)

                return f"Tax = Base + (Excess × Rate) = {base} + ({excess} × {progressive_rate}) = {tax}"

        return f"Error: No tax bracket found for value {value}"

    except Exception as e:
        return f"Error calculating progressive tax: {str(e)}"


@tool
def calculate_tax_relief(relief_items_json: str, relief_limits_json: str) -> str:
    """
    Calculates total allowable tax relief by applying limits to each item.

    Args:
        relief_items_json: JSON dict of relief items and claimed amounts.
                          Format: '{"medical": 8000, "education": 5000, "lifestyle": 3000}'
        relief_limits_json: JSON dict of maximum relief limits per category.
                           Format: '{"medical": 8000, "education": 7000, "lifestyle": 2500}'

    Returns:
        String with total allowable relief

    Example:
        calculate_tax_relief('{"medical":8000}', '{"medical":8000}')
    """
    try:
        import json

        relief_items = json.loads(relief_items_json)
        relief_limits = json.loads(relief_limits_json)

        total_relief = 0
        breakdown = []

        for item, claimed in relief_items.items():
            limit = relief_limits.get(item, 0)
            allowed = min(claimed, limit)
            total_relief += allowed

            breakdown.append(f"{item}: Claimed {claimed}, Limit {limit}, Allowed {allowed}")

        result = "\n".join(breakdown)
        result += f"\n\nTotal Allowable Relief: {total_relief}"

        return result

    except Exception as e:
        return f"Error calculating tax relief: {str(e)}"


@tool
def calculate_taxable_income(gross_income: float, total_relief: float) -> str:
    """
    Calculates taxable income after deducting relief.

    Args:
        gross_income: Gross income before relief
        total_relief: Total allowable relief

    Returns:
        String with taxable income

    Example:
        calculate_taxable_income(80000, 15000) returns 65000
    """
    try:
        taxable_income = gross_income - total_relief

        if taxable_income < 0:
            taxable_income = 0

        return f"Taxable Income = Gross Income - Relief = {gross_income} - {total_relief} = {taxable_income}"

    except Exception as e:
        return f"Error calculating taxable income: {str(e)}"
