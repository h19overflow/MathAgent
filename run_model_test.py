import argparse
import os
import asyncio
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from pydantic_ai import Agent, BinaryContent

# TODO , Implement text extraction from the image and pass it along the image to the model , this can be done usig ocr and it might enhance the accuracy of the model.


load_dotenv()

EXTRACTION_PROMPT = """
You are a mathematical visual extraction expert. Your ONLY job is to carefully analyze the image and extract structured information. DO NOT solve the problem.

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

Be extremely precise with coordinates and numerical values. When reading from a graph, verify your readings against the grid.
"""

SOLVER_PROMPT = """
You are an expert mathematical problem solver. You receive structured data extracted from a math problem and your job is to solve it step-by-step.

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
- Solve step-by-step with clear arithmetic
- Apply any qualitative constraints before finalizing
- Verify your solution makes sense in context

Step 4: Final Answer
- State the answer clearly
- Ensure it addresses ALL parts of the question
"""

VALIDATION_PROMPT = """
You are a rigorous mathematical validator. Check the solution for correctness.

Check:
1. Are all calculations arithmetically correct?
2. Does each step follow logically?
3. Are there any algebraic errors?
4. Does the final answer address the question fully?

OUTPUT FORMAT:
STATUS: [VALID/INVALID]
REASONING: [explanation]
FEEDBACK: [if INVALID, specific issues to fix]
"""


def initialize_extraction_agent(model_name: str) -> Agent:
    return Agent(model_name, system_prompt=EXTRACTION_PROMPT)

def initialize_solver_agent(model_name: str) -> Agent:
    return Agent(model_name, system_prompt=SOLVER_PROMPT)

def initialize_validation_agent(model_name: str) -> Agent:
    return Agent(model_name, system_prompt=VALIDATION_PROMPT)

async def extract_from_image(agent: Agent, image_path: str) -> tuple[str, int]:
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()

        extraction_request = "Analyze this mathematical problem image and extract all structured information following the format specified in your instructions."

        result = await agent.run([
            extraction_request,
            BinaryContent(data=image_data, media_type='image/png'),
        ])

        extracted_data = result.output
        tokens = 0

        if hasattr(result, 'usage'):
            usage = result.usage()
            tokens = usage.input_tokens + usage.output_tokens

        return extracted_data, tokens

    except Exception as e:
        return f"Error: {e}", 0

async def solve_from_extraction(agent: Agent, extracted_data: str, feedback: str = "") -> tuple[str, int]:
    try:
        solve_prompt = f"""Here is the structured data extracted from a mathematical problem:

{extracted_data}

Using this structured data, solve the problem step-by-step."""

        if feedback:
            solve_prompt += f"""

IMPORTANT - FEEDBACK FROM VALIDATION:
{feedback}

Please address these issues and solve correctly."""

        result = await agent.run(solve_prompt)

        solution = result.output
        tokens = 0

        if hasattr(result, 'usage'):
            usage = result.usage()
            tokens = usage.input_tokens + usage.output_tokens

        return solution, tokens

    except Exception as e:
        return f"Error: {e}", 0

async def validate_solution(agent: Agent, extracted_data: str, solution: str) -> tuple[bool, str, int]:
    try:
        validation_prompt = f"""Review this mathematical solution:

EXTRACTED DATA:
{extracted_data}

PROPOSED SOLUTION:
{solution}

Validate the solution following your instructions."""

        result = await agent.run(validation_prompt)

        validation_output = result.output
        tokens = 0

        if hasattr(result, 'usage'):
            usage = result.usage()
            tokens = usage.input_tokens + usage.output_tokens

        is_valid = "STATUS: VALID" in validation_output or "STATUS:VALID" in validation_output

        return is_valid, validation_output, tokens

    except Exception as e:
        return False, f"Validation Error: {e}", 0


async def process_test_images(input_csv: str, img_folder: str, output_csv: str, model_name: str):
    print(f"Reading CSV from {input_csv}...")
    df = pd.read_csv(input_csv)

    required_cols = ['image_filename', 'ground_truth', 'marking_scheme']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    df['extracted_data'] = ""
    df['llm_answer'] = ""
    df['tokens_used'] = 0
    df['status'] = ""
    df['model'] = ""
    df['validation_status'] = ""
    df['validation_attempts'] = 0
    df['validation_feedback'] = ""

    extractor = initialize_extraction_agent(model_name)
    solver = initialize_solver_agent(model_name)
    validator = initialize_validation_agent(model_name)

    total_tokens = 0
    max_attempts = 3

    print(f"\nProcessing {len(df)} images with 2-stage pipeline...")
    for idx, row in tqdm(df.iterrows(), total=len(df)):
        img_filename = row['image_filename']
        img_path = os.path.join(img_folder, img_filename)

        if not os.path.exists(img_path):
            print(f"\nWarning: Image not found: {img_path}")
            df.at[idx, 'llm_answer'] = "Image not found"
            df.at[idx, 'status'] = "ERROR"
            df.at[idx, 'model'] = model_name
            continue

        print(f"\nProcessing: {img_filename}")

        print("  Stage 1: Extracting structured data from image...")
        extracted_data, extraction_tokens = await extract_from_image(extractor, img_path)
        total_tokens += extraction_tokens

        if extracted_data.startswith("Error"):
            df.at[idx, 'extracted_data'] = extracted_data
            df.at[idx, 'llm_answer'] = "Extraction failed"
            df.at[idx, 'status'] = "ERROR"
            df.at[idx, 'model'] = model_name
            df.at[idx, 'tokens_used'] = extraction_tokens
            continue

        df.at[idx, 'extracted_data'] = extracted_data

        print("  Stage 2: Solving with validation loop...")
        feedback = ""
        final_solution = ""
        validation_status = "FAILED"
        solving_tokens = 0

        for attempt in range(1, max_attempts + 1):
            print(f"    Attempt {attempt}/{max_attempts}...")

            solution, solve_tokens = await solve_from_extraction(solver, extracted_data, feedback)
            solving_tokens += solve_tokens

            if solution.startswith("Error"):
                final_solution = solution
                validation_status = "ERROR"
                break

            print(f"    Validating solution...")
            is_valid, validation_output, validation_tokens = await validate_solution(validator, extracted_data, solution)
            solving_tokens += validation_tokens

            if is_valid:
                print(f"    ✓ Solution validated!")
                final_solution = solution
                validation_status = "VALID"
                break
            else:
                print(f"    ✗ Validation failed")
                feedback_start = validation_output.find("FEEDBACK:")
                if feedback_start != -1:
                    feedback = validation_output[feedback_start + 9:].strip()
                else:
                    feedback = validation_output

                final_solution = solution

                if attempt == max_attempts:
                    print(f"    Max attempts reached")
                    validation_status = "INVALID_MAX_ATTEMPTS"

        df.at[idx, 'llm_answer'] = final_solution
        df.at[idx, 'tokens_used'] = extraction_tokens + solving_tokens
        df.at[idx, 'status'] = "SUCCESS" if not final_solution.startswith("Error") else "ERROR"
        df.at[idx, 'model'] = model_name
        df.at[idx, 'validation_status'] = validation_status
        df.at[idx, 'validation_attempts'] = attempt
        df.at[idx, 'validation_feedback'] = feedback if validation_status != "VALID" else ""

        total_tokens += solving_tokens
        print(f"  Total tokens: {extraction_tokens + solving_tokens} | Running total: {total_tokens}")

    print(f"\nSaving results to {output_csv}...")
    df.to_csv(output_csv, index=False)

    print("\n" + "="*60)
    print("TEST SUMMARY - 2-STAGE PIPELINE")
    print("="*60)
    print(f"Total images processed: {len(df)}")
    print(f"Successful: {len(df[df['status'] == 'SUCCESS'])}")
    print(f"Errors: {len(df[df['status'] == 'ERROR'])}")
    print(f"\nValidation Results:")
    print(f"  Valid on first attempt: {len(df[df['validation_attempts'] == 1])}")
    print(f"  Valid after retry: {len(df[(df['validation_status'] == 'VALID') & (df['validation_attempts'] > 1)])}")
    print(f"  Failed validation: {len(df[df['validation_status'] == 'INVALID_MAX_ATTEMPTS'])}")
    print(f"  Validation errors: {len(df[df['validation_status'] == 'ERROR'])}")
    print(f"\nTotal tokens used: {total_tokens}")
    print(f"Results saved to: {output_csv}")
    print("="*60)

    return df

async def main(form_level: str):
    base_dir = os.getcwd()
    questions_dir = os.path.join(base_dir, "QAs")
    model_name = "gpt-5-mini"
    input_csv = os.path.join(questions_dir, f"test_questions_mathform{form_level}.csv")
    img_folder = os.path.join(questions_dir, "Soalan maths", f"form {form_level}")
    output_dir = os.path.join(questions_dir, model_name)  # Removed invalid { }
    output_csv = os.path.join(output_dir, f"test_results_form{form_level}_{model_name}_COT+StepBack.csv")

    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")
    if not os.path.exists(img_folder):
        raise FileNotFoundError(f"Image folder not found: {img_folder}")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    results_df = await process_test_images(input_csv, img_folder, output_csv, model_name)

    print("\nFirst 3 results:")
    print(results_df[['image_filename', 'ground_truth', 'llm_answer', 'status']].head(3))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--form", type=str, required=True, choices=["4", "5"], help="Form level: 4 or 5")
    args = parser.parse_args()
    asyncio.run(main(args.form))