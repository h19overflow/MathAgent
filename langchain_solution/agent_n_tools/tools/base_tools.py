"""
Number Base Tools
Purpose: Convert numbers between different bases (2-10) and validate base representations.
Role: Handles base conversion for word problems involving different number systems.
Dependencies: None (uses built-in Python functions)
"""

from langchain.tools import tool


@tool
def convert_base(number_string: str, from_base: int, to_base: int) -> str:
    """
    Converts a number from one base to another.

    Supports bases 2-10. Useful for problems involving different number systems.

    Args:
        number_string: The number as a string (e.g., "3300", "1101")
        from_base: Source base (2-10)
        to_base: Target base (2-10)

    Returns:
        String with conversion result in JSON format

    Example:
        convert_base("3300", 4, 10) converts 3300₄ to base 10
    """
    try:
        # Validate bases
        if not (2 <= from_base <= 10 and 2 <= to_base <= 10):
            return "Error: Bases must be between 2 and 10"

        # Validate number string for the source base
        valid_digits = set(str(i) for i in range(from_base))
        if not all(digit in valid_digits for digit in number_string):
            return f"Error: '{number_string}' contains invalid digits for base {from_base}"

        # Convert to base 10 first
        decimal_value = int(number_string, from_base)

        # Convert from base 10 to target base
        if to_base == 10:
            result = str(decimal_value)
        else:
            result = ""
            temp = decimal_value
            while temp > 0:
                result = str(temp % to_base) + result
                temp //= to_base
            if result == "":
                result = "0"

        import json
        output = {
            "original_number": number_string,
            "original_base": from_base,
            "target_base": to_base,
            "result": result
        }

        return json.dumps(output, indent=2)

    except ValueError as e:
        return f"Error: Invalid number '{number_string}' for base {from_base}"
    except Exception as e:
        return f"Error converting base: {str(e)}"


@tool
def validate_number_in_base(number_string: str, base: int) -> str:
    """
    Checks if a number is valid in a given base.

    Args:
        number_string: The number to validate (e.g., "234", "1089")
        base: The base to check (2-10)

    Returns:
        String indicating whether the number is valid

    Example:
        validate_number_in_base("345", 4) returns False (5 is invalid in base 4)
    """
    try:
        if not (2 <= base <= 10):
            return f"Error: Base must be between 2 and 10"

        valid_digits = set(str(i) for i in range(base))

        if all(digit in valid_digits for digit in number_string):
            return f"✓ '{number_string}' is VALID in base {base}"
        else:
            invalid_digits = [d for d in number_string if d not in valid_digits]
            return f"✗ '{number_string}' is NOT valid in base {base}. Invalid digits: {invalid_digits}"

    except Exception as e:
        return f"Error validating number: {str(e)}"


@tool
def convert_base_list(numbers_json: str, from_base: int, to_base: int) -> str:
    """
    Converts multiple numbers from one base to another.

    Args:
        numbers_json: JSON string list of numbers (e.g., '["123", "456", "789"]')
        from_base: Source base (2-10)
        to_base: Target base (2-10)

    Returns:
        String with all conversion results

    Example:
        convert_base_list('["10", "20", "30"]', 4, 10) converts multiple base-4 numbers
    """
    try:
        import json

        numbers = json.loads(numbers_json)

        if not isinstance(numbers, list):
            return "Error: Input must be a JSON list of numbers"

        results = []
        for num in numbers:
            num_str = str(num)
            # Convert each number
            decimal_value = int(num_str, from_base)

            if to_base == 10:
                result = str(decimal_value)
            else:
                result = ""
                temp = decimal_value
                while temp > 0:
                    result = str(temp % to_base) + result
                    temp //= to_base
                if result == "":
                    result = "0"

            results.append(f"{num_str}₍{from_base}₎ = {result}₍{to_base}₎")

        return "Conversions:\n" + "\n".join(results)

    except Exception as e:
        return f"Error converting list: {str(e)}"
