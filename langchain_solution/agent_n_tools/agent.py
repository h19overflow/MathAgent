"""
Math Agent with Two-Stage Pipeline
Purpose: Extract structured data from images, then solve using mathematical tools.
Role: Mimics run_model_test.py architecture with extraction → solving pattern.
"""

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage,BaseMessage,ToolMessage
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


# Solver prompt (from run_model_test.py adapted for LangChain tools)
SOLVER_PROMPT = """You are an expert mathematical problem solver equipped with specialized tools for algebra, statistics, and geometry.

CRITICAL RULES:
1. For optimization problems (shortest path, minimum cost, etc.), ALWAYS check the CONSTRAINTS section first
2. Qualitative constraints (e.g., "safer", "more reliable") may override standard optimization
3. When working with graphs, double-check that extracted coordinates produce the correct line equations
4. For inequalities, verify the direction (≤ vs ≥) matches the shaded region description
5. Show ALL calculation steps explicitly

SOLVING PROCESS:

Step 1: Problem Understanding
- Restate what needs to be found
- Identify if there are any non-standard constraints from the problem text

Step 2: Mathematical Formulation
- Convert visual data into mathematical expressions
- For graphs: derive line equations from coordinates
- For inequalities: determine inequality signs from shading
- For networks: identify relevant paths and calculate totals

Step 3: Solution Execution
- Use your available tools to verify calculations
- Apply any qualitative constraints before finalizing
- Verify your solution makes sense in context

Step 4: Final Answer
- State the answer clearly
- Ensure it addresses ALL parts of the question

IMPORTANT: After completing all steps, provide your FINAL ANSWER in this format:
FINAL ANSWER: [Your complete answer here]

Once you provide the FINAL ANSWER above, STOP and do not call any more tools."""


class MathAgent:
    """
    Two-stage Math Agent for Form 4/5 problems.

    Stage 1: Extraction Agent - extracts structured data from images
    Stage 2: Solver Agent - solves problems using mathematical tools

    Tools available in solver:
    - SymPy Solver: equation solving, simplification, expansion, factoring
    - NumPy Calculator: sum, mean, variance, std dev, percentages, frequency
    - Inequality     print("Problem 1: Algebra")undary checking
    - Statistics Utils: grouped data analysis, cumulative frequency
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

        # Create solver agent (with all math tools)
        self.solver_agent = create_agent(
            model=self.model_name,
            tools=MATH_TOOLS,
            system_prompt=SOLVER_PROMPT,
        )

    def extract_from_image(self, image_path: str) -> Tuple[str, int]:
        """
        Extract structured data from a mathematical problem image.

        Args:
            image_path: Path to the image file

        Returns:
            Tuple of (extracted_data, token_count)
        """
        logger.debug(f"extract_from_image called with: {image_path}")
        try:
            # Check file exists
            if not os.path.exists(image_path):
                error_msg = f"Image not found at {image_path}"
                logger.error(error_msg)
                return f"Error: {error_msg}", 0

            logger.debug(f"✓ Image file exists")

            # Read and encode image
            logger.debug(f"Reading and encoding image...")
            file_size = os.path.getsize(image_path)
            logger.debug(f"  File size: {file_size} bytes")

            with open(image_path, 'rb') as f:
                image_data = base64.standard_b64encode(f.read()).decode('utf-8')

            logger.debug(f"  ✓ Image encoded. Base64 length: {len(image_data)}")

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
            logger.debug(f"  Media type: {media_type}")

            # Create message with image
            logger.debug(f"Creating HumanMessage with multimodal content...")
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
            logger.debug(f"  ✓ Message created with {len(message.content)} content blocks")

            # Invoke extraction agent
            logger.info(f"Invoking extraction agent with model: {self.model_name}")
            logger.debug(f"  Extraction agent type: {type(self.extraction_agent)}")

            try:
                result = self.extraction_agent.invoke(
                    {"messages": [message]},
                    config={"recursion_limit": 5}  # Low limit for extraction (no tools needed)
                )
                logger.debug(f"  ✓ Agent invocation completed")
            except GraphRecursionError as e:
                logger.error(f"✗ RECURSION LIMIT REACHED: {str(e)}", exc_info=True)
                # Try to get partial result if available
                try:
                    result = e.result if hasattr(e, 'result') else {"messages": []}
                    save_agent_output("extraction", result, error_type="RECURSION_LIMIT")
                except Exception as save_err:
                    logger.error(f"Failed to save recursion error output: {str(save_err)}")
                return f"Error: Extraction recursion limit reached. {str(e)}", 0
            except Exception as e:
                logger.error(f"✗ Extraction error: {str(e)}", exc_info=True)
                return f"Error extracting from image: {str(e)}", 0
            logger.debug(f"  Result type: {type(result)}")
            logger.debug(f"  Result keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")

            # Extract the response
            extracted_data = ""
            if "messages" in result:
                logger.debug(f"  Processing messages from result...")
                messages = result["messages"]
                logger.debug(f"    Total messages: {len(messages)}")
                final_message = messages[-1]
                logger.debug(f"    Final message type: {type(final_message)}")

                # Handle both dict and message object types
                if hasattr(final_message, 'get'):
                    extracted_data = final_message.get("content", str(result))
                elif hasattr(final_message, 'content'):
                    extracted_data = final_message.content
                else:
                    extracted_data = str(result)

                logger.debug(f"    ✓ Extracted data length: {len(str(extracted_data))}")
            else:
                logger.warning(f"  'messages' key not found in result")
                logger.debug(f"  Result: {str(result)[:500]}")
                extracted_data = str(result)

            logger.info(f"✓ Extraction successful")
            return extracted_data, 0  # Token count to be implemented

        except Exception as e:
            error_msg = f"Error extracting from image: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return error_msg, 0

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
            logger.info(f"Invoking solver agent with model: {self.model_name}")
            logger.debug(f"  Solver agent type: {type(self.solver_agent)}")

            try:
                result = self.solver_agent.invoke(
                    {"messages": [{"role": "user", "content": solve_prompt}]},
                    config={"recursion_limit": 20}  # Allows multiple tool calls but prevents infinite loops
                )
                logger.debug(f"  ✓ Solver invocation completed")
            except GraphRecursionError as e:
                logger.error(f"✗ RECURSION LIMIT REACHED: {str(e)}", exc_info=True)
                # Try to get partial result if available
                try:
                    result = e.result if hasattr(e, 'result') else {"messages": []}
                    try:
                        self.saveToolMessages(result.get("messages", []))
                    except Exception as e:
                        logger.error(f'Unable to save tool Messages:{e}')
                    save_agent_output("solver", result, error_type="RECURSION_LIMIT")
                except Exception as save_err:
                    logger.error(f"Failed to save recursion error output: {str(save_err)}")
                return f"Error: Solver recursion limit reached after {e}. Check agent_outputs/ for message history.", 0
            except Exception as e:
                logger.error(f"✗ Solver error: {str(e)}", exc_info=True)
                return f"Error solving from extraction: {str(e)}", 0

            # Extract the response
            solution = ""
            if "messages" in result:
                logger.debug(f"Processing messages from result...")
                messages = result["messages"]
                logger.debug(f"  Total messages: {len(messages)}")
                final_message = messages[-1]
                logger.debug(f"  Final message type: {type(final_message)}")

                # Handle both dict and message object types
                if hasattr(final_message, 'get'):
                    solution = final_message.get("content", str(result))
                elif hasattr(final_message, 'content'):
                    solution = final_message.content
                else:
                    solution = str(final_message)

                logger.debug(f"  ✓ Solution extracted. Length: {len(str(solution))}")

            return solution, 0  # Token count to be implemented

        except Exception as e:
            logger.error(f"Unexpected error in solve_from_extraction: {str(e)}", exc_info=True)
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

            if extracted_data.startswith("Error"):
                return {
                    "extracted_data": extracted_data,
                    "llm_answer": "Extraction failed",
                    "tokens_used": extraction_tokens,
                    "status": "ERROR",
                    "model": self.model_name,
                }

            # Stage 2: Solve
            solution, solve_tokens = self.solve_from_extraction(extracted_data)

            return {
                "extracted_data": extracted_data,
                "llm_answer": solution,
                "tokens_used": extraction_tokens + solve_tokens,
                "status": "SUCCESS" if not solution.startswith("Error") else "ERROR",
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
            Save tool call messages to a log file for debugging.

            Args:
                messages: List of BaseMessage objects containing tool calls
            """
            toolMessages = []
            try:
                logger.debug(f"Saving tool messages...")
                for message in messages:
                    if isinstance(message, ToolMessage):
                     for tool_call in message.tool_calls or message.content or []:
                        logger.debug(f"Tool Call - Name: {tool_call.name}, Args: {tool_call.args}")
                        toolMessages.append({
                            "tool_name": tool_call.name,
                            "args": tool_call.args
                        })
                if not toolMessages:
                    logger.debug("No tool messages found to save.")
                    return
                with open("tool_messages_log.json", "w") as f:
                    json.dump(toolMessages, f, indent=2)
                logger.info(f"✓ Tool messages saved to tool_messages_log.json")
            except Exception as e:
                logger.error(f"Error saving tool messages: {str(e)}", exc_info=True)

