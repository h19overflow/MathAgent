"""
Math Agent with Two-Stage Pipeline
Purpose: Extract structured data from images, then solve using mathematical tools.
Role: Mimics run_model_test.py architecture with extraction → solving pattern.
"""

from langchain.agents import create_agent
# from langchain.agents.middleware import LLMToolSelectorMiddleware  # Disabled - compatibility issues
from langchain.agents.middleware import ModelCallLimitMiddleware
from langchain_core.messages import HumanMessage,BaseMessage,ToolMessage,AIMessage
from tools import MATH_TOOLS
from dotenv import load_dotenv
from langgraph.errors import GraphRecursionError
import base64
import os
import logging
import json
from typing import Tuple, List
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Configure logging for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def save_agent_output(stage: str, result: dict, error_type: str = None) -> str:
    """
    Save agent output/error to a nicely formatted file.

    Args:
        stage: "extraction" or "solver"
        result: The result dict from agent.invoke() or error context
        error_type: Type of error (e.g., "RECURSION_LIMIT", "EXCEPTION")

    Returns:
        Path to saved file
    """
    output_dir = "agent_outputs"
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    error_marker = f"_{error_type}" if error_type else ""
    filename = f"agent_output_{stage}{error_marker}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)

    output_data = {
        "timestamp": datetime.now().isoformat(),
        "stage": stage,
        "error_type": error_type,
        "messages": []
    }

    # Extract and format messages
    if isinstance(result, dict) and "messages" in result:
        for i, msg in enumerate(result["messages"], 1):
            msg_dict = {
                "index": i,
                "type": msg.__class__.__name__,
                "content": ""
            }

            # Handle different message types
            if hasattr(msg, 'content'):
                content = msg.content
                if isinstance(content, str):
                    msg_dict["content"] = content
                elif isinstance(content, list):
                    msg_dict["content"] = str(content)
                else:
                    msg_dict["content"] = str(content)
            elif isinstance(msg, dict):
                msg_dict["content"] = msg.get("content", str(msg))
            else:
                msg_dict["content"] = str(msg)

            # Add metadata if available
            if hasattr(msg, 'tool_calls'):
                msg_dict["tool_calls"] = [
                    {"tool_name": tc.name, "args": tc.args}
                    for tc in msg.tool_calls
                ] if msg.tool_calls else []

            output_data["messages"].append(msg_dict)

    # Save to file
    with open(filepath, "w") as f:
        json.dump(output_data, f, indent=2)

    logger.info(f"✓ Agent output saved to: {filepath}")
    return filepath


# Extraction prompt (from run_model_test.py adapted for LangChain)
EXTRACTION_PROMPT = """You are a mathematical visual extraction expert. Your ONLY job is to carefully analyze the image and extract structured information. DO NOT solve the problem.

Your task is to extract:

1. PROBLEM TYPE: Identify the mathematical domain (e.g., "Linear Inequalities Graph", "Network Graph Theory", "Motion Graph", "Geometry", "Statistics")

2. QUESTION TEXT: Extract ALL text from the question word-for-word, including:
   - Main question
   - Any contextual information (e.g., "safer route", "fastest path")
   - Any constraints or conditions mentioned
   - Sub-questions (a, b, c, etc.)

3. VISUAL ELEMENTS: Based on the diagram type, extract:

   For GRAPHS (inequalities, motion, functions):
   - Identify ALL lines/curves in the graph
   - For each line: Extract at least 2 clear points as coordinates (x, y)
   - Note line style: solid, dashed, thick
   - Note shaded regions (above/below lines, left/right of vertical lines)
   - Extract axis labels, scale, and units
   - Read ALL labeled points precisely from the grid

   For NETWORKS:
   - List ALL nodes (vertices) with their labels
   - List ALL edges with their weights/distances
   - Note any special markings (arrows, colors, highlighted paths)

   For GEOMETRIC FIGURES:
   - Identify shapes and their properties
   - Extract all measurements, angles, labels
   - Note parallel lines, equal angles, congruent sides

   For DATA/STATISTICS:
   - Extract all data points from tables, charts, histograms
   - Note axes, scales, units, frequencies

4. CRITICAL CONSTRAINTS: Extract any qualitative requirements that might override standard optimization:
   - Safety requirements
   - Time constraints
   - Specific conditions mentioned in the text

OUTPUT FORMAT (use this exact structure):
---
PROBLEM TYPE: [type]

QUESTION:
[full question text]

VISUAL DATA:
[structured extraction based on diagram type]

CONSTRAINTS:
[any special conditions or requirements]
---

Be extremely precise with coordinates and numerical values. When reading from a graph, verify your readings against the grid."""


# Solver prompt (adapted for LangChain tools with SPM Form 4/5 focus)
SOLVER_PROMPT = """You are an expert SPM mathematics problem solver with access to specialized tools covering all Form 4/5 topics.

AVAILABLE TOOLS - Use these to solve problems accurately:
• Quadratic Functions: analyze_quadratic, solve_quadratic_equation, find_quadratic_vertex
• Number Bases: convert_base, validate_number_in_base
• Sequences: analyze_sequence (AP/GP detection), find_nth_term
• Sets/Venn Diagrams: solve_venn_diagram, set operations (union, intersection, complement)
• Graph Theory: analyze_graph_properties, find_shortest_path (Dijkstra)
• Motion Graphs: calculate_motion_gradient, calculate_motion_area
• Statistics: calculate_ungrouped_statistics, calculate_quartiles, calculate_iqr
• Probability: generate_sample_space, calculate_probability
• Financial: analyze_budget, calculate_savings_rate
• Variation: solve_variation (direct/inverse/joint)
• Matrices: multiply_matrices, solve_matrix_equation
• Insurance/Tax: calculate_premium, calculate_progressive_tax
• Geometry: solve_enlargement, calculate_scale_factor_from_lengths
• Trigonometry: solve_right_triangle, solve_trig_equation
• Modeling: fit_quadratic_model, fit_linear_model
• Inequalities: convert_region_to_inequality, validate_point_in_inequality

CRITICAL RULES:
1. ALWAYS use the appropriate tools for calculations - don't compute manually
2. LIMIT tool usage - typically need 1-3 tool calls max per problem
3. For optimization (shortest path, min cost), check CONSTRAINTS first - qualitative factors may override
4. For graphs: verify extracted coordinates produce correct equations
5. For inequalities: verify direction (≤ vs ≥) matches shaded region
6. Show ALL steps explicitly with tool-verified calculations
7. STOP immediately after providing FINAL ANSWER - no more tool calls allowed

SOLVING PROCESS:

Step 1: Problem Understanding (NO TOOLS NEEDED)
- Identify problem type (quadratic, graph theory, statistics, etc.)
- Restate what needs to be found
- Check for non-standard constraints

Step 2: Tool Selection & Mathematical Formulation (NO TOOLS NEEDED)
- Choose 1-3 most appropriate tools based on problem type
- Convert visual data into tool-compatible format (JSON strings for lists/dicts)
- Prepare all tool inputs before making any calls

Step 3: Solution Execution with Tools (MAKE TOOL CALLS HERE)
- Call only the essential tools (usually 1-3 calls total)
- Verify tool outputs make sense
- Apply qualitative constraints before finalizing
- DO NOT call tools repeatedly - get what you need in 1-3 calls

Step 4: Final Answer (NO MORE TOOLS)
- State answer clearly addressing ALL parts
- Verify solution matches problem context
- IMMEDIATELY provide FINAL ANSWER and STOP

STOPPING CONDITION - You MUST stop when ANY of these occur:
1. You have provided the "FINAL ANSWER:" response
2. You have made 3+ tool calls
3. You have enough information to answer the question
4. You are repeating the same tool calls

IMPORTANT: After completing all steps, provide your FINAL ANSWER in this EXACT format:
FINAL ANSWER: [Your complete answer here]

Once you type "FINAL ANSWER:" you MUST STOP IMMEDIATELY. Do NOT call any more tools after this."""


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

        # Create extraction agent (no tools needed)
        self.extraction_agent = create_agent(
            model=self.model_name,
            tools=[],  # Extraction uses vision only
            system_prompt=EXTRACTION_PROMPT,
        )

        # Create solver agent (with all math tools + call limit middleware)
        # ModelCallLimitMiddleware prevents infinite loops by limiting tool calls per run
        self.solver_agent = create_agent(
            model=self.model_name,
            tools=MATH_TOOLS,
            system_prompt=SOLVER_PROMPT,
            middleware=[
                ModelCallLimitMiddleware(
                    run_limit=15,  # Max 15 model calls per problem (prevents infinite loops)
                    exit_behavior="end",  # Gracefully stop instead of raising error
                ),
            ],
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

            # Extract the response
            extracted_data = ""
            if "messages" in result:
                messages = result["messages"]
                final_message = messages[-1]

                # Handle both dict and message object types
                if hasattr(final_message, 'get'):
                    extracted_data = final_message.get("content", str(result))
                elif hasattr(final_message, 'content'):
                    extracted_data = final_message.content
                else:
                    extracted_data = str(result)
            else:
                extracted_data = str(result)

            # Ensure extracted_data is always a string
            if isinstance(extracted_data, list):
                extracted_data = str(extracted_data)
            elif not isinstance(extracted_data, str):
                extracted_data = str(extracted_data)

            logger.info(f"[EXTRACTION] ✓ Completed")
            return extracted_data, 0  # Token count to be implemented

        except Exception as e:
            logger.error(f"[EXTRACTION] Unexpected error: {str(e)}", exc_info=True)
            return f"Error extracting from image: {str(e)}", 0

    def solve_from_extraction(self, extracted_data: str) -> Tuple[str, int]:
        """
        Solve a problem from extracted structured data.

        Args:
            extracted_data: The structured data extracted from an image or provided directly

        Returns:
            Tuple of (solution, token_count)
        """
        try:
            solve_prompt = f"""Here is the structured data extracted from a mathematical problem:

{extracted_data}
Using this structured data, solve the problem step-by-step following the SOLVING PROCESS:
Step 1: Problem Understanding
- Restate what needs to be found
- Identify if there are any non-standard constraints from the problem text
Step 2: Solution Execution
- Solve step-by-step with clear arithmetic
- Apply any qualitative constraints before finalizing
- Verify your solution makes sense in context
Step 3: Final Answer
- State the answer clearly
- Ensure it addresses ALL parts of the question

IMPORTANT: After completing all steps, provide your FINAL ANSWER in this format:
FINAL ANSWER: [Your complete answer here]

Once you provide the FINAL ANSWER above, STOP and do not call any more tools."""

            # Invoke solver agent
            logger.info(f"[SOLVER] Starting")

            try:
                result = self.solver_agent.invoke(
                    {"messages": [{"role": "user", "content": solve_prompt}]},
                    config={"recursion_limit": 50}  # Higher limit to allow complex multi-step problems
                )

                # Save tool calls from successful execution
                try:
                    self.saveToolMessages(result.get("messages", []))
                except Exception as e:
                    logger.error(f'[SOLVER] Unable to save tool messages: {e}')

            except GraphRecursionError as e:
                logger.error(f"[SOLVER] Recursion limit exceeded", exc_info=True)
                # Try to get partial result if available
                try:
                    result = e.result if hasattr(e, 'result') else {"messages": []}
                    try:
                        self.saveToolMessages(result.get("messages", []))
                    except Exception as e:
                        logger.error(f'[SOLVER] Unable to save tool messages: {e}')
                    save_agent_output("solver", result, error_type="RECURSION_LIMIT")
                except Exception as save_err:
                    logger.error(f"[SOLVER] Failed to save error output: {str(save_err)}")
                return f"Error: Solver recursion limit reached after {e}. Check agent_outputs/ for message history.", 0
            except Exception as e:
                logger.error(f"[SOLVER] Failed: {str(e)}", exc_info=True)
                return f"Error solving from extraction: {str(e)}", 0

            # Extract the response
            solution = ""
            if "messages" in result:
                messages = result["messages"]
                final_message = messages[-1]

                # Handle both dict and message object types
                if hasattr(final_message, 'get'):
                    solution = final_message.get("content", str(result))
                elif hasattr(final_message, 'content'):
                    solution = final_message.content
                else:
                    solution = str(final_message)

            # Ensure solution is always a string
            if isinstance(solution, list):
                solution = str(solution)
            elif not isinstance(solution, str):
                solution = str(solution)

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
            Dictionary with extracted_data, llm_answer, tokens_used, status, model
        """
        try:
            # Stage 1: Extract
            extracted_data, extraction_tokens = self.extract_from_image(image_path)

            # Ensure extracted_data is a string (sometimes it's a list)
            if isinstance(extracted_data, list):
                extracted_data = str(extracted_data)

            if isinstance(extracted_data, str) and extracted_data.startswith("Error"):
                return {
                    "extracted_data": extracted_data,
                    "llm_answer": "Extraction failed",
                    "tokens_used": extraction_tokens,
                    "status": "ERROR",
                    "model": self.model_name,
                }

            # Stage 2: Solve
            solution, solve_tokens = self.solve_from_extraction(extracted_data)

            # Ensure solution is a string
            if isinstance(solution, list):
                solution = str(solution)

            return {
                "extracted_data": extracted_data,
                "llm_answer": solution,
                "tokens_used": extraction_tokens + solve_tokens,
                "status": "SUCCESS" if not (isinstance(solution, str) and solution.startswith("Error")) else "ERROR",
                "model": self.model_name,
            }

        except Exception as e:
            return {
                "extracted_data": str(e),
                "llm_answer": f"Error: {str(e)}",
                "tokens_used": 0,
                "status": "ERROR",
                "model": self.model_name,
            }
    def saveToolMessages(self, messages : List[BaseMessage] ) -> None:
            """
            Save tool call messages to a log file for debugging in tool_calls/ directory.

            Args:
                messages: List of BaseMessage objects containing tool calls
            """
            toolMessages = []
            try:
                # Extract tool calls from AIMessage objects
                for message in messages:
                    if isinstance(message, AIMessage) and hasattr(message, 'tool_calls'):
                        if message.tool_calls:
                            for tool_call in message.tool_calls:
                                # Handle both dict and object formats
                                if isinstance(tool_call, dict):
                                    toolMessages.append({
                                        "name": tool_call.get('name'),
                                        "args": tool_call.get('args'),
                                        "id": tool_call.get('id', None)
                                    })
                                else:
                                    toolMessages.append({
                                        "name": tool_call.name,
                                        "args": tool_call.args,
                                        "id": getattr(tool_call, 'id', None)
                                    })

                if not toolMessages:
                    return

                # Create tool_calls directory in same location as this script
                script_dir = os.path.dirname(os.path.abspath(__file__))
                tool_calls_dir = os.path.join(script_dir, "tool_calls")
                os.makedirs(tool_calls_dir, exist_ok=True)

                # Save with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = os.path.join(tool_calls_dir, f"tool_calls_{timestamp}.json")

                with open(filepath, "w") as f:
                    json.dump(toolMessages, f, indent=2)
                logger.info(f"[TOOLS] Saved {len(toolMessages)} tool calls to tool_calls/")
            except Exception as e:
                logger.error(f"[TOOLS] Error saving tool calls: {str(e)}", exc_info=True)

