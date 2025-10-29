"""
Financial Management Tools
Purpose: Analyze personal budgets and financial plans.
Role: Calculates income, expenses, and surplus/deficit.
Dependencies: None (uses basic arithmetic)
"""

from langchain.tools import tool


@tool
def analyze_budget(income_json: str, expenses_json: str) -> str:
    """
    Analyzes a personal budget by calculating totals and net cash flow.

    Args:
        income_json: JSON string list of income items with 'source' and 'amount'.
                    Format: '[{"source": "Salary", "amount": 3800}, ...]'
        expenses_json: JSON string list of expense items with 'item' and 'amount'.
                      Format: '[{"item": "Rent", "amount": 800}, ...]'

    Returns:
        String with JSON-formatted budget analysis

    Example:
        analyze_budget('[{"source":"Salary","amount":5000}]', '[{"item":"Rent","amount":1000}]')
    """
    try:
        import json

        income_items = json.loads(income_json)
        expense_items = json.loads(expenses_json)

        # Calculate totals
        total_income = sum(item['amount'] for item in income_items)
        total_expenses = sum(item['amount'] for item in expense_items)

        net_cash_flow = total_income - total_expenses

        status = "Surplus" if net_cash_flow > 0 else "Deficit" if net_cash_flow < 0 else "Balanced"

        result = {
            "total_income": round(total_income, 2),
            "total_expenses": round(total_expenses, 2),
            "net_cash_flow": round(net_cash_flow, 2),
            "status": status
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return f"Error analyzing budget: {str(e)}"


@tool
def calculate_savings_rate(income: float, expenses: float) -> str:
    """
    Calculates the savings rate as a percentage of income.

    Args:
        income: Total income
        expenses: Total expenses

    Returns:
        String with savings rate percentage

    Example:
        calculate_savings_rate(5000, 3000) returns 40% savings rate
    """
    try:
        if income == 0:
            return "Error: Income cannot be zero"

        savings = income - expenses
        savings_rate = (savings / income) * 100

        return f"Savings: {savings}, Savings Rate: {savings_rate:.2f}%"

    except Exception as e:
        return f"Error calculating savings rate: {str(e)}"


@tool
def check_budget_viability(income: float, expenses: float, min_surplus: float = 0) -> str:
    """
    Checks if a budget is viable (income covers expenses plus minimum surplus).

    Args:
        income: Total income
        expenses: Total expenses
        min_surplus: Minimum required surplus (default: 0)

    Returns:
        String indicating budget viability

    Example:
        check_budget_viability(5000, 4800, 200) checks for at least 200 surplus
    """
    try:
        net_cash_flow = income - expenses

        if net_cash_flow >= min_surplus:
            return f"✓ Budget is viable. Net cash flow: {net_cash_flow} (Required: {min_surplus})"
        else:
            shortfall = min_surplus - net_cash_flow
            return f"✗ Budget not viable. Shortfall: {shortfall} (Net: {net_cash_flow}, Required: {min_surplus})"

    except Exception as e:
        return f"Error checking viability: {str(e)}"
