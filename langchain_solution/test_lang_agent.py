"""
LangChain Math Agent Test Runner
Purpose: Test the LangChain-based math agent on Form 4/5 problems using a two-stage pipeline.
This script mimics run_model_test.py but uses LangChain agents with mathematical tools.
"""

import argparse
import os
import pandas as pd
from tqdm import tqdm
from pathlib import Path

# Add parent directory to path to import agent_n_tools
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agent_n_tools'))

from langchain_solution.agent_n_tools.agent import MathAgent


def initialize_math_agent(model_name: str) -> MathAgent:
    """Initialize the LangChain Math Agent."""
    return MathAgent(model=model_name)


def process_test_images(
    input_csv: str,
    img_folder: str,
    output_csv: str,
    model_name: str = "google-genai:gemini-2.5-flash-lite"
) -> pd.DataFrame:
    """
    Process test images using the LangChain Math Agent.

    Args:
        input_csv: Path to input CSV with test questions
        img_folder: Path to folder containing test images
        output_csv: Path to output CSV for results
        model_name: LLM model to use (default: Claude 3.5 Sonnet)

    Returns:
        DataFrame with results
    """
    # Read input CSV
    print(f"Reading CSV from {input_csv}...")
    if input_csv.endswith('.csv'):
        df = pd.read_csv(input_csv)
    elif input_csv.endswith('.xlsx'):
        df = pd.read_excel(input_csv)
    else:
        raise ValueError("Input file must be a CSV or Excel file.")

    # Validate required columns
    required_cols = ['image_filename', 'ground_truth', 'marking_scheme']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Add result columns
    df['extracted_data'] = ""
    df['llm_answer'] = ""
    df['tokens_used'] = 0
    df['status'] = ""
    df['model'] = ""

    # Initialize agent
    agent = initialize_math_agent(model_name)

    total_tokens = 0

    print(f"\nProcessing {len(df)} images with 2-stage pipeline (Extraction → Solving)...")
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

        # Process image through two-stage pipeline
        print("  Stage 1: Extracting structured data from image...")
        print("  Stage 2: Solving with mathematical tools...")

        result = agent.process_image(img_path)

        # Store results
        df.at[idx, 'extracted_data'] = result['extracted_data']
        df.at[idx, 'llm_answer'] = result['llm_answer']
        df.at[idx, 'tokens_used'] = result['tokens_used']
        df.at[idx, 'status'] = result['status']
        df.at[idx, 'model'] = result['model']

        total_tokens += result['tokens_used']
        print(f"  Status: {result['status']} | Tokens: {result['tokens_used']} | Running total: {total_tokens}")

    # Save results to CSV
    print(f"\nSaving results to {output_csv}...")
    os.makedirs(os.path.dirname(output_csv) if os.path.dirname(output_csv) else '.', exist_ok=True)
    df.to_csv(output_csv, index=False)

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY - 2-STAGE LANGCHAIN PIPELINE")
    print("=" * 60)
    print(f"Total images processed: {len(df)}")
    print(f"Successful: {len(df[df['status'] == 'SUCCESS'])}")
    print(f"Errors: {len(df[df['status'] == 'ERROR'])}")
    print(f"Total tokens used: {total_tokens}")
    print(f"Results saved to: {output_csv}")
    print("=" * 60)

    return df


async def main(form_level: str):
    """Main entry point for testing."""
    base_dir = os.getcwd()
    questions_dir = os.path.join(base_dir, "QAs")
    model_name = "google-genai:gemini-2.5-flash-lite"

    input_csv = os.path.join(questions_dir, f"test_questions_mathform{form_level}.csv")
    img_folder = os.path.join(questions_dir, "Soalan maths", f"form {form_level}")
    output_dir = os.path.join(questions_dir, "langchain_results")
    output_csv = os.path.join(output_dir, f"test_results_form{form_level}_{model_name}_langchain_agent.csv")

    # Validate input files exist
    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")
    if not os.path.exists(img_folder):
        raise FileNotFoundError(f"Image folder not found: {img_folder}")

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Process images
    results_df = process_test_images(input_csv, img_folder, output_csv, model_name)

    # Display first few results
    print("\nFirst 3 results:")
    print(results_df[['image_filename', 'ground_truth', 'status', 'llm_answer']].head(3))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test LangChain Math Agent on Form 4/5 problems"
    )
    parser.add_argument(
        "--form",
        type=str,
        required=True,
        choices=["4", "5"],
        help="Form level: 4 or 5"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="claude-3-5-sonnet-20241022",
        help="LLM model to use (default: claude-3-5-sonnet-20241022)"
    )
    args = parser.parse_args()

    import asyncio
    asyncio.run(main(args.form))
