"""
Math Agent with Two-Stage Pipeline
Purpose: Extract structured data from images, then solve using mathematical tools.
Role: Mimics run_model_test.py architecture with extraction → solving pattern.
"""

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from tools import MATH_TOOLS
import base64
import os
from typing import  Tuple


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
- Ensure it addresses ALL parts of the question"""


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

    def __init__(self, model: str = "google-genai:gemini-2.5-flash-lite"):
        """
        Initialize the two-stage Math Agent.

        Args:
            model: The LLM model to use (default: Claude 3.5 Sonnet)
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
        try:
            if not os.path.exists(image_path):
                return f"Error: Image not found at {image_path}", 0

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
            result = self.extraction_agent.invoke(
                {"messages": [message]}
            )

            # Extract the response
            extracted_data = ""
            if "messages" in result:
                final_message = result["messages"][-1]
                extracted_data = final_message.get("content", str(result))

            return extracted_data, 0  # Token count to be implemented

        except Exception as e:
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

Step 2: Mathematical Formulation
- Convert visual data into mathematical expressions
- For graphs: derive line equations from coordinates
- For inequalities: determine inequality signs from shading
- For networks: identify relevant paths and calculate totals

Step 3: Solution Execution
- Solve step-by-step with clear arithmetic
- Apply any qualitative constraints before finalizing
- Verify your solution makes sense in context

Step 4: Final Answer
- State the answer clearly
- Ensure it addresses ALL parts of the question"""

            # Invoke solver agent
            result = self.solver_agent.invoke(
                {"messages": [{"role": "user", "content": solve_prompt}]}
            )

            # Extract the response
            solution = ""
            if "messages" in result:
                final_message = result["messages"][-1]
                solution = final_message.get("content", str(result))

            return solution, 0  # Token count to be implemented

        except Exception as e:
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



#
# # Example usage
# if __name__ == "__main__":
#     # Initialize the agent
#     agent = MathAgent()
#
#     # Example 1: Text-only problem (legacy mode)
#     problem1 = """
#     Solve the equation: 2x + 5 = 15
#     """
#
#     print("Example 1: Text-Only Problem (Algebra)")
#     print("-" * 50)
#     print(f"Problem: {problem1}")
#     print("\nSolution:")
#     print(agent.solve(problem1))
#     print("\n" + "=" * 50 + "\n")
#
#     # Example 2: Statistics problem
#     problem2 = """
#     For a grouped frequency distribution:
#     Class: [10-20), [20-30), [30-40), [40-50)
#     Frequency: 5, 10, 8, 3
#
#     Calculate:
#     a) Σfx (sum of frequency × midpoint)
#     b) Σfx² (sum of frequency × midpoint²)
#     c) Variance and standard deviation
#     """
#
#     print("Example 2: Statistics Problem")
#     print("-" * 50)
#     print(f"Problem: {problem2}")
#     print("\nSolution:")
#     print(agent.solve(problem2))
#     print("\n" + "=" * 50 + "\n")
#
#     # Example 3: Inequality validation
#     problem3 = """
#     Given the inequality: x + y ≤ 5
#
#     a) Check if the boundary line should be solid or dashed
#     b) Validate these points:
#        - (1, 2)
#        - (3, 3)
#        - (5, 0)
#     """
#
#     print("Example 3: Inequality Problem")
#     print("-" * 50)
#     print(f"Problem: {problem3}")
#     print("\nSolution:")
#     print(agent.solve(problem3))
#     print("\n" + "=" * 50 + "\n")
#
#     # Example 4: Image processing (if image exists)
#     print("Example 4: Image Processing (Two-Stage Pipeline)")
#     print("-" * 50)
#     test_image = "sample_math_problem.png"
#     if os.path.exists(test_image):
#         result = agent.process_image(test_image)
#         print(f"Status: {result['status']}")
#         print(f"Extracted Data:\n{result['extracted_data'][:500]}...")
#         print(f"\nSolution:\n{result['llm_answer'][:500]}...")
#     else:
#         print(f"No test image found at {test_image}")
