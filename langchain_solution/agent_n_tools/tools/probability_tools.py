"""
Probability Tools
Purpose: Generate sample spaces and calculate probabilities for combined events.
Role: Lists all possible outcomes and computes probability of events.
Dependencies: itertools for combinations
"""

from langchain.tools import tool
from itertools import product


@tool
def generate_sample_space(events_json: str) -> str:
    """
    Generates the complete sample space for multiple probabilistic events.

    Lists all possible outcome combinations when multiple events occur.

    Args:
        events_json: JSON string list of event objects with 'name' and 'outcomes'.
                    Format: '[{"name": "Box_K", "outcomes": ["S", "E", "R"]}, ...]'

    Returns:
        String with JSON-formatted sample space

    Example:
        generate_sample_space('[{"name":"Coin","outcomes":["H","T"]}]')
    """
    try:
        import json

        events = json.loads(events_json)

        # Extract outcome lists
        outcome_lists = [event['outcomes'] for event in events]

        # Generate all combinations using Cartesian product
        sample_space = list(product(*outcome_lists))

        result = {
            "sample_space_size": len(sample_space),
            "sample_space": [list(outcome) for outcome in sample_space]
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return f"Error generating sample space: {str(e)}"


@tool
def calculate_probability(favorable_outcomes: int, total_outcomes: int) -> str:
    """
    Calculates probability as favorable outcomes / total outcomes.

    Args:
        favorable_outcomes: Number of favorable outcomes
        total_outcomes: Total number of possible outcomes

    Returns:
        String with probability as fraction and decimal

    Example:
        calculate_probability(3, 12) returns P = 3/12 = 0.25
    """
    try:
        if total_outcomes == 0:
            return "Error: Total outcomes cannot be zero"

        probability = favorable_outcomes / total_outcomes

        # Simplify fraction
        from math import gcd
        divisor = gcd(favorable_outcomes, total_outcomes)
        simplified_num = favorable_outcomes // divisor
        simplified_den = total_outcomes // divisor

        return f"P = {simplified_num}/{simplified_den} = {probability:.4f}"

    except Exception as e:
        return f"Error calculating probability: {str(e)}"


@tool
def count_favorable_outcomes(sample_space_json: str, condition: str) -> str:
    """
    Counts outcomes in a sample space that satisfy a condition.

    Args:
        sample_space_json: JSON string of sample space (list of outcome lists).
                          Format: '[["H", "1"], ["H", "2"], ["T", "1"], ...]'
        condition: Description of the condition to check (e.g., "first element is H")

    Returns:
        String with count of favorable outcomes

    Note: This is a helper - agent should filter the sample space based on condition

    Example:
        count_favorable_outcomes('[["H","1"],["T","2"]]', 'explained by agent')
    """
    try:
        import json

        sample_space = json.loads(sample_space_json)

        return f"Sample space has {len(sample_space)} outcomes. Agent should filter based on: {condition}"

    except Exception as e:
        return f"Error: {str(e)}"


@tool
def calculate_combined_probability(prob_a: float, prob_b: float,
                                   operation: str = "and") -> str:
    """
    Calculates probability of combined events (independent events).

    Args:
        prob_a: Probability of event A (0 to 1)
        prob_b: Probability of event B (0 to 1)
        operation: "and" for P(A and B) = P(A) × P(B),
                  "or" for P(A or B) = P(A) + P(B) - P(A) × P(B)

    Returns:
        String with combined probability

    Example:
        calculate_combined_probability(0.5, 0.3, "and") for independent events
    """
    try:
        if not (0 <= prob_a <= 1 and 0 <= prob_b <= 1):
            return "Error: Probabilities must be between 0 and 1"

        if operation == "and":
            result = prob_a * prob_b
            return f"P(A and B) = P(A) × P(B) = {prob_a} × {prob_b} = {result:.4f}"

        elif operation == "or":
            result = prob_a + prob_b - (prob_a * prob_b)
            return f"P(A or B) = P(A) + P(B) - P(A)×P(B) = {prob_a} + {prob_b} - {prob_a * prob_b} = {result:.4f}"

        else:
            return "Error: operation must be 'and' or 'or'"

    except Exception as e:
        return f"Error calculating combined probability: {str(e)}"
