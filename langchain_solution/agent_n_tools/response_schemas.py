"""
Response Schemas for Math Agent
Purpose: Define structured Pydantic models for agent responses
Role: Ensures proper validation and type safety for agent outputs
Dependencies: pydantic
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class ExtractionResponse(BaseModel):
    """
    Structured response from the image extraction agent.

    Ensures the agent returns properly formatted extraction data with:
    - Validated category from predefined list
    - Complete extracted problem text
    - Confidence score for quality assurance
    """

    category: str = Field(
        ...,
        description="Mathematical problem category. Must be one of: "
        "ALGEBRA_EQUATIONS, GEOMETRY_SPATIAL, DISCRETE_MATH, "
        "STATISTICS, LINEAR_ALGEBRA, APPLIED_MATH, or GENERAL",
        examples=["ALGEBRA_EQUATIONS", "GEOMETRY_SPATIAL"]
    )

    extracted_data: str = Field(
        ...,
        description="Complete extracted problem text including question, visual data, and constraints. "
        "Include all numerical values, variable names, and diagram descriptions."
    )

    confidence: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="Confidence score (0-1) indicating how confident the extraction is. "
        "Lower scores when visual quality is poor or problem is ambiguous."
    )

    notes: Optional[str] = Field(
        default=None,
        description="Optional notes about extraction quality or issues encountered"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "category": "QUADRATIC_EQUATIONS",
                "extracted_data": "PROBLEM TYPE: Quadratic Equations\n\nQUESTION: Solve x² + 5x + 6 = 0\n\nVISUAL DATA: None",
                "confidence": 0.95,
                "notes": "Clear text, straightforward problem"
            }
        }


class SolutionStep(BaseModel):
    """
    Single step in the solution process.

    Tracks each computational step with clear explanations.
    """

    step_number: int = Field(
        ...,
        ge=1,
        description="Step number in the solution sequence"
    )

    description: str = Field(
        ...,
        description="Clear description of what this step accomplishes"
    )

    calculation: Optional[str] = Field(
        default=None,
        description="Mathematical calculation or formula applied in this step"
    )

    result: Optional[str] = Field(
        default=None,
        description="Result or output from this step"
    )


class SolvingResponse(BaseModel):
    """
    Structured response from the problem solving agent.

    Provides comprehensive solution with:
    - Problem understanding confirmation
    - Step-by-step solution process
    - Final answer in requested format
    - Confidence assessment
    """

    problem_understanding: str = Field(
        ...,
        description="Brief statement confirming understanding of what the problem asks. "
        "Should address the specific question being asked."
    )

    solution_approach: str = Field(
        ...,
        description="Description of the approach/strategy used to solve the problem. "
        "E.g., 'Using quadratic formula', 'Applying Dijkstra's algorithm', etc."
    )

    solution_steps: List[SolutionStep] = Field(
        ...,
        min_items=1,
        description="Ordered list of solution steps from start to final answer"
    )

    final_answer: str = Field(
        ...,
        description="The final answer to the problem. Should be clear, complete, and address "
        "all parts of the question. Include units if applicable."
    )

    reasoning: str = Field(
        ...,
        description="Brief explanation of why this answer makes sense and whether "
        "it satisfies any constraints mentioned in the problem"
    )

    confidence: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="Confidence score (0-1) in the correctness of the solution. "
        "Lower if problem was ambiguous or solution is uncertain."
    )

    alternative_methods: Optional[List[str]] = Field(
        default=None,
        description="Optional list of alternative methods that could solve this problem"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "problem_understanding": "Find the roots of the quadratic equation x² + 5x + 6 = 0",
                "solution_approach": "Using quadratic formula to find the roots",
                "solution_steps": [
                    {
                        "step_number": 1,
                        "description": "Identify coefficients",
                        "calculation": "a = 1, b = 5, c = 6",
                        "result": "Coefficients identified"
                    },
                    {
                        "step_number": 2,
                        "description": "Apply quadratic formula",
                        "calculation": "x = (-5 ± √(25-24)) / 2 = (-5 ± 1) / 2",
                        "result": "x = -2 or x = -3"
                    }
                ],
                "final_answer": "x = -2 or x = -3",
                "reasoning": "Both solutions satisfy the original equation when substituted",
                "confidence": 0.98,
                "alternative_methods": ["Factoring: (x+2)(x+3)=0"]
            }
        }


class ErrorResponse(BaseModel):
    """
    Structured error response for failed agent execution.

    Provides consistent error reporting across both agents.
    """

    error_type: str = Field(
        ...,
        description="Type of error: EXTRACTION_FAILED, RECURSION_LIMIT, PARSING_ERROR, etc."
    )

    error_message: str = Field(
        ...,
        description="Detailed error message explaining what went wrong"
    )

    partial_data: Optional[str] = Field(
        default=None,
        description="Any partial data recovered before the error occurred"
    )

    recovery_suggestion: Optional[str] = Field(
        default=None,
        description="Suggestion for resolving or working around the error"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "error_type": "RECURSION_LIMIT",
                "error_message": "Agent recursion limit of 50 exceeded while solving problem",
                "partial_data": "Problem identified as quadratic equation type",
                "recovery_suggestion": "Try simplifying the problem or increasing recursion limit"
            }
        }
