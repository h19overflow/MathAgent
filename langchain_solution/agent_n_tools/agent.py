"""
Math Agent with Two-Stage Pipeline
Purpose: Extract structured data from images, then solve using mathematical tools.
Role: Mimics run_model_test.py architecture with extraction → solving pattern.
"""
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_core.messages import HumanMessage
from .response_schemas import ExtractionResponse, SolvingResponse
from dotenv import load_dotenv
from langgraph.errors import GraphRecursionError
import base64
import os
import logging
from typing import Tuple
from langchain_solution.agent_n_tools.prompts.solver_extractor_prompts import SOLVER_PROMPT, EXTRACTION_PROMPT, \
    solve_prompt
from langchain_solution.agent_n_tools.save_agent_outputs import save_agent_output , saveToolMessages
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables from .env file
load_dotenv()

# Configure logging for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class MathAgent:
    """
    Two-stage Math Agent for SPM Form 4/5 problems.

    Stage 1: Extraction Agent - extracts structured data from images
    Stage 2: Solver Agent - solves problems using specialized mathematical tools

    The solver has access to 50+ specialized tools covering all SPM Form 4/5 topics.
    The system prompt guides the model to select and use only the most relevant tools
    for each specific problem type.

    Available tool categories (SPM Form 4/5 aligned):
    1. Quadratic Functions: analyze_quadratic, solve_quadratic_equation, find_quadratic_vertex
    2. Number Base Conversions: convert_base, validate_number_in_base, convert_base_list
    3. Sequences (AP/GP): analyze_sequence, find_nth_term
    4. Sets & Venn Diagrams: solve_venn_diagram, calculate_set_union, calculate_set_intersection
    5. Graph Theory: analyze_graph_properties, find_shortest_path, calculate_graph_degree
    6. Motion Graphs: calculate_motion_gradient, calculate_motion_area, analyze_uniform_motion
    7. Statistics (Ungrouped): calculate_ungrouped_statistics, calculate_quartiles, calculate_iqr
    8. Probability: generate_sample_space, calculate_probability, calculate_combined_probability
    9. Financial Management: analyze_budget, calculate_savings_rate, check_budget_viability
    10. Variation: solve_variation (direct, inverse, direct_square, inverse_square, joint)
    11. Matrices: multiply_matrices, solve_matrix_equation, calculate_matrix_determinant
    12. Insurance/Taxation: calculate_premium, calculate_progressive_tax, calculate_tax_relief
    13. Geometry & Enlargement: solve_enlargement, calculate_scale_factor_from_lengths
    14. Trigonometry: solve_right_triangle, solve_trig_equation, calculate_trig_ratio
    15. Mathematical Modeling: fit_quadratic_model, fit_linear_model, evaluate_model
    16. Linear Inequalities: convert_region_to_inequality, validate_point_in_inequality
    """

    def __init__(self, model: str = "google_genai:gemini-2.5-flash-lite"):
        """
        Initialize the two-stage Math Agent.

        Args:
            model: The LLM model to use as a string identifier (default: google_genai:gemini-2.5-flash-lite)
                   Supported formats:
                   - "anthropic:claude-3-5-sonnet-20241022" (requires ANTHROPIC_API_KEY)
                   - "google_genai:gemini-2.5-flash-lite" (requires GOOGLE_API_KEY)
                   - "openai:gpt-4o" (requires OPENAI_API_KEY)

                   All environment variables are loaded from .env file automatically.
        """
        self.model_name = model
        self.model = ChatGoogleGenerativeAI(model=self.model_name,temperature=0.3,max_output_tokens=2000,)
        # Create extraction agent with structured output
        self.extraction_agent = create_agent(
            model=self.model_name,
            tools=[],  # Extraction uses vision only
            system_prompt=EXTRACTION_PROMPT,
            response_format=ToolStrategy(ExtractionResponse),
        )

        # Solver agent will be created dynamically based on problem category
        # See _create_solver_agent() method below

    def _create_solver_agent(self, category: str):
        """
        Create a focused solver agent for a specific mathematical category.

        Args:
            category: One of ALGEBRA_EQUATIONS, GEOMETRY_SPATIAL, DISCRETE_MATH,
                     STATISTICS, LINEAR_ALGEBRA, APPLIED_MATH, or GENERAL

        Returns:
            Configured solver agent with category-specific tools and prompt
        """
        from .prompts import SOLVER_PROMPTS
        from .tools import TOOL_CATEGORIES, MATH_TOOLS

        # Get tools for this category
        if category in TOOL_CATEGORIES:
            tools = TOOL_CATEGORIES[category]
            if tools is None:  # GENERAL category uses all tools
                tools = MATH_TOOLS
        else:
            # Invalid category, fallback to all tools
            logger.warning(f"[SOLVER] Unknown category '{category}', using all tools")
            category = "GENERAL"
            tools = MATH_TOOLS

        # Get prompt for this category
        prompt = SOLVER_PROMPTS.get(category, SOLVER_PROMPTS["GENERAL"])

        # Log category selection
        tool_count = len(tools) if tools else 0
        logger.info(f"[SOLVER] Creating solver for category '{category}' with {tool_count} tools")

        # Create focused solver agent with structured output
        return create_agent(
            model=self.model_name,
            tools=tools,
            system_prompt=prompt,
            response_format=ToolStrategy(SolvingResponse),

        )

    def extract_from_image(self, image_path: str) -> Tuple[str, int]:
        """
        Extract structured data from a mathematical problem image.

        Args:
            image_path: Path to the image file

        Returns:
            Tuple of (extracted_data, token_count)
        """
        try:
            # Check file exists
            if not os.path.exists(image_path):
                error_msg = f"Image not found at {image_path}"
                logger.error(error_msg)
                return f"Error: {error_msg}", 0

            # Read and encode image
            with open(image_path, 'rb') as f:
                image_data = base64.standard_b64encode(f.read()).decode('utf-8')

            # Determine image media type
            ext = os.path.splitext(image_path)[1].lower()
            media_type_map = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.webp': 'image/webp',
            }
            media_type = media_type_map.get(ext, 'image/png')

            # Create message with image
            message = HumanMessage(
                content=[
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{media_type};base64,{image_data}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "Analyze this mathematical problem image and extract all structured information following the format specified in your instructions."
                    }
                ]
            )

            # Invoke extraction agent
            logger.info(f"[EXTRACTION] Starting: {os.path.basename(image_path)}")

            try:
                result = self.extraction_agent.invoke(
                    {"messages": [message]},
                    config={"recursion_limit": 5}  # Low limit for extraction (no tools needed)
                )
            except GraphRecursionError as e:
                logger.error(f"[EXTRACTION] Recursion limit exceeded", exc_info=True)
                # Try to get partial result if available
                try:
                    result = e.result if hasattr(e, 'result') else {"messages": []}
                    save_agent_output("extraction", result, error_type="RECURSION_LIMIT")
                except Exception as save_err:
                    logger.error(f"[EXTRACTION] Failed to save error output: {str(save_err)}")
                return f"Error: Extraction recursion limit reached. {str(e)}", 0
            except Exception as e:
                logger.error(f"[EXTRACTION] Failed: {str(e)}", exc_info=True)
                return f"Error extracting from image: {str(e)}", 0

            # Extract structured response
            category = "GENERAL"  # Default fallback
            extracted_data = ""  # Default fallback

            try:
                # Check for structured response from ToolStrategy
                if "structured_response" in result:
                    structured = result["structured_response"]

                    if isinstance(structured, ExtractionResponse):
                        # Direct Pydantic model object
                        category = structured.category
                        extracted_data = structured.extracted_data
                        confidence = structured.confidence

                        # Validate category
                        valid_categories = ["ALGEBRA_EQUATIONS", "GEOMETRY_SPATIAL", "DISCRETE_MATH",
                                            "STATISTICS", "LINEAR_ALGEBRA", "APPLIED_MATH", "GENERAL"]
                        if category not in valid_categories:
                            logger.warning(f"[EXTRACTION] Invalid category '{category}', using GENERAL")
                            category = "GENERAL"

                        logger.info(f"[EXTRACTION] ✓ Category detected: {category} (confidence: {confidence:.2f})")
                    else:
                        logger.warning(f"[EXTRACTION] Unexpected structured response type: {type(structured)}")
                        extracted_data = str(structured)
                else:
                    logger.error('Extraction from the image is NOT structured')

            except Exception as e:
                logger.error(f"[EXTRACTION] Error extracting structured response: {str(e)}", exc_info=True)
                extracted_data = str(result)

            logger.info(f"[EXTRACTION] ✓ Completed")
            # Return tuple: (category, extracted_data, token_count)
            return (category, extracted_data), 0  # Token count to be implemented

        except Exception as e:
            logger.error(f"[EXTRACTION] Unexpected error: {str(e)}", exc_info=True)
            return f"Error extracting from image: {str(e)}", 0

    def solve_from_extraction(self, extraction_result, category: str = None) -> Tuple[str, int]:
        """
        Solve a problem from extracted structured data.

        Args:
            extraction_result: Either a tuple of (category, extracted_data) or just extracted_data string
            category: Optional category override (if extraction_result is just a string)

        Returns:
            Tuple of (solution, token_count)
        """
        try:
            # Parse extraction result to get category and data
            if isinstance(extraction_result, tuple) and len(extraction_result) == 2:
                category, extracted_data = extraction_result
            else:
                # Legacy format: just extracted_data string
                extracted_data = extraction_result
                if category is None:
                    category = "GENERAL"
                    logger.warning(f"[SOLVER] No category provided, using GENERAL")

            logger.info(f"[SOLVER] Problem category: {category}")

            # Create focused solver for this category
            solver_agent = self._create_solver_agent(category)
            # Invoke solver agent
            logger.info(f"[SOLVER] Starting with category-specific agent")
            try:
                result = solver_agent.invoke(
                    {"messages": [{"role": "user", "content": solve_prompt.format(extracted_data=extracted_data)}]},
                    config={"recursion_limit": 50}  # Higher limit to allow complex multi-step problems
                )
                # Save tool calls from successful execution
                try:
                    saveToolMessages(result.get("messages", []))
                except Exception as e:
                    logger.error(f'[SOLVER] Unable to save tool messages: {e}')

            except GraphRecursionError as e:
                logger.error(f"[SOLVER] Recursion limit exceeded", exc_info=True)
                # Try to get partial result if available
                try:
                    result = e.result if hasattr(e, 'result') else {"messages": []}
                    try:
                        saveToolMessages(result.get("messages", []))
                    except Exception as e:
                        logger.error(f'[SOLVER] Unable to save tool messages: {e}')
                    save_agent_output("solver", result, error_type="RECURSION_LIMIT")
                except Exception as save_err:
                    logger.error(f"[SOLVER] Failed to save error output: {str(save_err)}")
                return f"Error: Solver recursion limit reached after {e}. Check agent_outputs/ for message history.", 0
            except Exception as e:
                logger.error(f"[SOLVER] Failed: {str(e)}", exc_info=True)
                return f"Error solving from extraction: {str(e)}", 0

            # Extract structured response
            solution = ""
            try:
                # Check for structured response from ToolStrategy
                if "structured_response" in result:
                    structured = result["structured_response"]

                    if isinstance(structured, SolvingResponse):
                        # Direct Pydantic model object
                        # Format the solution nicely
                        solution_text = f"Problem Understanding: {structured.problem_understanding}\n\n"
                        solution_text += f"Solution Approach: {structured.solution_approach}\n\n"
                        solution_text += "Solution Steps:\n"
                        for step in structured.solution_steps:
                            solution_text += f"  Step {step.step_number}: {step.description}\n"
                            if step.calculation:
                                solution_text += f"    Calculation: {step.calculation}\n"
                            if step.result:
                                solution_text += f"    Result: {step.result}\n"
                        solution_text += f"\nReasoning: {structured.reasoning}\n"
                        solution_text += f"\nFINAL ANSWER: {structured.final_answer}\n"
                        solution_text += f"(Confidence: {structured.confidence:.2f})"
                        solution = solution_text

                        logger.info(
                            f"[SOLVER] ✓ Structured response extracted (confidence: {structured.confidence:.2f})")

                # Ensure solution is always a string
                if isinstance(solution, list):
                    solution = str(solution)
                elif not isinstance(solution, str):
                    solution = str(solution)

            except Exception as e:
                logger.error(f"[SOLVER] Error extracting structured response: {str(e)}", exc_info=True)
                solution = str(result)

            logger.info(f"[SOLVER] ✓ Completed")
            return solution, 0  # Token count to be implemented

        except Exception as e:
            logger.error(f"[SOLVER] Unexpected error: {str(e)}", exc_info=True)
            return f"Error solving from extraction: {str(e)}", 0

    def process_image(self, image_path: str) -> dict:
        """
        Complete pipeline: extract from image, then solve.

        Args:
            image_path: Path to the image file

        Returns:
            Dictionary with extracted_data, llm_answer, category, tokens_used, status, model
        """
        try:
            # Stage 1: Extract (returns (category, extracted_data), tokens)
            extraction_result, extraction_tokens = self.extract_from_image(image_path)

            # Parse extraction result
            if isinstance(extraction_result, tuple) and len(extraction_result) == 2:
                category, extracted_data = extraction_result
            else:
                # Handle legacy format or error
                if isinstance(extraction_result, str) and extraction_result.startswith("Error"):
                    return {
                        "extracted_data": extraction_result,
                        "llm_answer": "Extraction failed",
                        "category": "UNKNOWN",
                        "tokens_used": extraction_tokens,
                        "status": "ERROR",
                        "model": self.model_name,
                    }
                # Legacy string format
                category = "GENERAL"
                extracted_data = extraction_result
                logger.warning(f"[PIPELINE] Extraction returned legacy format, using GENERAL category")

            # Ensure extracted_data is a string
            if isinstance(extracted_data, list):
                extracted_data = str(extracted_data)

            logger.info(f"[PIPELINE] Category: {category}, proceeding to solve")

            # Stage 2: Solve (pass the tuple)
            solution, solve_tokens = self.solve_from_extraction((category, extracted_data))

            # Ensure solution is a string
            if isinstance(solution, list):
                solution = str(solution)

            return {
                "extracted_data": extracted_data,
                "llm_answer": solution,
                "category": category,
                "tokens_used": extraction_tokens + solve_tokens,
                "status": "SUCCESS" if not (isinstance(solution, str) and solution.startswith("Error")) else "ERROR",
                "model": self.model_name,
            }

        except Exception as e:
            logger.error(f"[PIPELINE] Error: {str(e)}", exc_info=True)
            return {
                "extracted_data": str(e),
                "llm_answer": f"Error: {str(e)}",
                "category": "ERROR",
                "tokens_used": 0,
                "status": "ERROR",
                "model": self.model_name,
            }
