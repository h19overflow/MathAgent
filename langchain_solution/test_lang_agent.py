"""
LangChain Math Agent Test Runner
Purpose: Test the LangChain-based math agent on Form 4/5 problems using a two-stage pipeline.
This script mimics run_model_test.py but uses LangChain agents with mathematical tools.
"""

import argparse
import os
import sys
import logging
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"math_agent_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# File handler (INFO level - important stuff and errors)
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.INFO)

# Console handler (INFO level - important stuff)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.info("=" * 80)
logger.info("LangChain Math Agent Test Runner Started")
logger.info(f"Log file: {LOG_FILE}")
logger.info("=" * 80)

# Add parent directory to path to import agent_n_tools
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agent_n_tools'))

from langchain_solution.agent_n_tools.agent import MathAgent

logger.debug("MathAgent imported successfully")


def initialize_math_agent(model_name: str) -> MathAgent:
    """Initialize the LangChain Math Agent."""
    logger.info(f"Initializing MathAgent with model: {model_name}")
    try:
        agent = MathAgent(model=model_name)
        logger.debug("MathAgent initialized successfully")
        return agent
    except Exception as e:
        logger.error(f"Failed to initialize MathAgent: {str(e)}", exc_info=True)
        raise


def process_test_images(
    input_csv: str,
    img_folder: str,
    output_csv: str,
    model_name: str = "google_genai:gemini-2.5-flash-lite"
) -> pd.DataFrame:
    """
    Process test images using the LangChain Math Agent with comprehensive logging.

    Args:
        input_csv: Path to input CSV with test questions
        img_folder: Path to folder containing test images
        output_csv: Path to output CSV for results
        model_name: LLM model to use

    Returns:
        DataFrame with results
    """
    logger.info(f"Starting process_test_images")
    logger.info(f"  Input CSV: {input_csv}")
    logger.info(f"  Image folder: {img_folder}")
    logger.info(f"  Output CSV: {output_csv}")
    logger.info(f"  Model: {model_name}")

    # Read input CSV
    logger.info(f"Reading input CSV from {input_csv}...")
    try:
        if input_csv.endswith('.csv'):
            df = pd.read_csv(input_csv)
        elif input_csv.endswith('.xlsx'):
            df = pd.read_excel(input_csv)
        else:
            raise ValueError("Input file must be a CSV or Excel file.")

        # Reset index to ensure sequential integer indexing (0, 1, 2, ...)
        df = df.reset_index(drop=True)
        logger.info(f"✓ CSV loaded. Total rows: {len(df)}")
        logger.debug(f"DataFrame index: {df.index.tolist()[:5]}... (first 5)")
    except Exception as e:
        logger.error(f"Failed to read input CSV: {str(e)}", exc_info=True)
        raise

    # Validate required columns
    required_cols = ['image_filename', 'ground_truth', 'marking_scheme']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        logger.error(f"Missing required columns: {missing_cols}")
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Add result columns
    df['extracted_data'] = ""
    df['llm_answer'] = ""
    df['tokens_used'] = 0
    df['status'] = ""
    df['model'] = ""

    # Initialize agent
    try:
        agent = initialize_math_agent(model_name)
    except Exception as e:
        logger.error(f"Failed to initialize agent: {str(e)}", exc_info=True)
        raise

    total_tokens = 0
    successful = 0
    failed = 0

    logger.info(f"Processing {len(df)} images with 2-stage pipeline (Extraction → Solving)...")

    for row_idx, row in tqdm(df.iterrows(), total=len(df)):
        # Use iloc for explicit integer-location based indexing (more reliable than iterrows index)
        iloc_idx = row_idx
        img_filename = row['image_filename']
        img_path = os.path.join(img_folder, img_filename)

        # Check if image exists
        if not os.path.exists(img_path):
            error_msg = f"Image not found at path: {img_path}"
            logger.error(f"[{iloc_idx+1}/{len(df)}] ✗ {error_msg}")
            df.iloc[iloc_idx, df.columns.get_loc('llm_answer')] = error_msg
            df.iloc[iloc_idx, df.columns.get_loc('status')] = "ERROR"
            df.iloc[iloc_idx, df.columns.get_loc('model')] = model_name
            failed += 1
            logger.debug(f"[{iloc_idx+1}/{len(df)}] Row {iloc_idx} marked as ERROR (image not found)")
            continue

        try:
            logger.debug(f"[{iloc_idx+1}/{len(df)}] Processing {img_filename}...")
            result = agent.process_image(img_path)

            # Validate result structure
            required_keys = ['extracted_data', 'llm_answer', 'tokens_used', 'status', 'model']
            missing_keys = [k for k in required_keys if k not in result]
            if missing_keys:
                logger.warning(f"[{iloc_idx+1}/{len(df)}] Result missing keys: {missing_keys}")

            # Store results using iloc (safer than using at with row index from iterrows)
            logger.debug(f"[{iloc_idx+1}/{len(df)}] Writing results to row {iloc_idx}...")
            df.iloc[iloc_idx, df.columns.get_loc('extracted_data')] = result['extracted_data']
            df.iloc[iloc_idx, df.columns.get_loc('llm_answer')] = result['llm_answer']
            tokens = result['tokens_used']
            df.iloc[iloc_idx, df.columns.get_loc('tokens_used')] = tokens
            status = result['status']
            df.iloc[iloc_idx, df.columns.get_loc('status')] = status
            df.iloc[iloc_idx, df.columns.get_loc('model')] = result['model']

            total_tokens += tokens

            # Verify write was successful
            written_answer = df.iloc[iloc_idx, df.columns.get_loc('llm_answer')]
            if written_answer == result['llm_answer']:
                logger.debug(f"[{iloc_idx+1}/{len(df)}] ✓ Row {iloc_idx} written successfully")
            else:
                logger.warning(f"[{iloc_idx+1}/{len(df)}] ⚠ Row {iloc_idx} write verification failed!")

            # Track success/failure
            if status == "SUCCESS":
                successful += 1
                logger.info(f"[{iloc_idx+1}/{len(df)}] ✓ {img_filename}")
            else:
                failed += 1
                logger.warning(f"[{iloc_idx+1}/{len(df)}] ✗ {img_filename} - {result['llm_answer'][:100]}")

        except Exception as e:
            logger.error(f"[{iloc_idx+1}/{len(df)}] Exception processing {img_filename}: {str(e)}", exc_info=True)
            df.iloc[iloc_idx, df.columns.get_loc('llm_answer')] = f"Exception: {str(e)}"
            df.iloc[iloc_idx, df.columns.get_loc('status')] = "ERROR"
            df.iloc[iloc_idx, df.columns.get_loc('model')] = model_name
            failed += 1
            logger.debug(f"[{iloc_idx+1}/{len(df)}] Row {iloc_idx} marked as ERROR (exception)")

    # Save results to CSV
    logger.info(f"\n{'='*80}")
    logger.info(f"Saving results to CSV: {output_csv}")
    try:
        # Ensure output directory exists
        output_dir_path = os.path.dirname(output_csv) if os.path.dirname(output_csv) else '.'
        os.makedirs(output_dir_path, exist_ok=True)
        logger.debug(f"Output directory ensured: {output_dir_path}")

        # Validate dataframe before saving
        rows_with_data = df['llm_answer'].notna().sum()
        logger.info(f"DataFrame stats before save: {len(df)} total rows, {rows_with_data} with answers")
        logger.debug(f"Sample data from row 0: {df.iloc[0][['image_filename', 'llm_answer']].to_dict() if len(df) > 0 else 'N/A'}")

        # Save to CSV
        df.to_csv(output_csv, index=False)
        logger.info(f"✓ Results saved to {output_csv}")

        # Verify file was created
        if not os.path.exists(output_csv):
            raise FileNotFoundError(f"Output file was not created: {output_csv}")
        file_size = os.path.getsize(output_csv)
        logger.info(f"✓ File verified - Size: {file_size} bytes")

        # Verify file contains expected data by reading it back
        logger.debug(f"Verifying file contents...")
        verify_df = pd.read_csv(output_csv)
        verify_rows_with_data = verify_df['llm_answer'].notna().sum()
        logger.info(f"✓ Verification: {len(verify_df)} rows loaded, {verify_rows_with_data} with answers")

        if verify_rows_with_data != rows_with_data:
            logger.warning(f"⚠ Data mismatch after save! Before: {rows_with_data}, After: {verify_rows_with_data}")
        else:
            logger.info(f"✓ Data integrity verified - all {rows_with_data} answers present")

    except Exception as e:
        logger.error(f"Failed to save results to CSV: {str(e)}", exc_info=True)
        raise

    # Print and log summary
    summary = f"""
{'='*80}
TEST SUMMARY - 2-STAGE LANGCHAIN PIPELINE
{'='*80}
Total images processed: {len(df)}
Successful: {successful}
Errors: {failed}
Success rate: {(successful/len(df)*100):.1f}%
Total tokens used: {total_tokens}
Results saved to: {output_csv}
Log file: {LOG_FILE}
{'='*80}
"""
    print(summary)
    logger.info(summary)

    return df


async def main(form_level: str, model_name: str = None):
    """Main entry point for testing with comprehensive logging."""
    logger.info(f"\n{'='*80}")
    logger.info("MAIN: Starting test configuration")
    logger.info(f"{'='*80}")

    # Get directories
    base_dir = os.getcwd()
    logger.info(f"Base directory: {base_dir}")

    questions_dir = os.path.join(base_dir, "QAs")
    logger.debug(f"Questions directory: {questions_dir}")

    # Determine model to use
    logger.info(f"Model selection priority:")
    if model_name is not None:
        logger.info(f"  1. ✓ Using provided argument: {model_name}")
    else:
        env_model = os.getenv("MODEL_NAME")
        if env_model:
            logger.info(f"  1. ✗ No argument provided")
            logger.info(f"  2. ✓ Using environment variable MODEL_NAME: {env_model}")
            model_name = env_model
        else:
            logger.info(f"  1. ✗ No argument provided")
            logger.info(f"  2. ✗ No environment variable MODEL_NAME")
            logger.info(f"  3. ✓ Using default: google_genai:gemini-2.5-flash-lite")
            model_name = "google_genai:gemini-2.5-flash-lite"

    logger.info(f"Final model choice: {model_name}")

    # Check API keys for selected model
    logger.info(f"\nAPI Key status:")
    if "google" in model_name.lower():
        api_key = os.getenv("GOOGLE_API_KEY")
        key_status = "✓ Set" if api_key else "✗ NOT SET"
        logger.info(f"  GOOGLE_API_KEY: {key_status}")
        if not api_key:
            logger.warning("  WARNING: GOOGLE_API_KEY is not set! This will likely cause errors.")
    elif "anthropic" in model_name.lower():
        api_key = os.getenv("ANTHROPIC_API_KEY")
        key_status = "✓ Set" if api_key else "✗ NOT SET"
        logger.info(f"  ANTHROPIC_API_KEY: {key_status}")
        if not api_key:
            logger.warning("  WARNING: ANTHROPIC_API_KEY is not set! This will likely cause errors.")
    elif "openai" in model_name.lower():
        api_key = os.getenv("OPENAI_API_KEY")
        key_status = "✓ Set" if api_key else "✗ NOT SET"
        logger.info(f"  OPENAI_API_KEY: {key_status}")
        if not api_key:
            logger.warning("  WARNING: OPENAI_API_KEY is not set! This will likely cause errors.")

    # Build file paths
    logger.info(f"\nFile paths:")
    input_csv = os.path.join(questions_dir, f"test_questions_mathform{form_level}.csv")
    logger.info(f"  Input CSV: {input_csv}")

    img_folder = os.path.join(questions_dir, "Soalan maths", f"form {form_level}")
    logger.info(f"  Image folder: {img_folder}")

    output_dir = os.path.join(questions_dir, "langchain_results")
    logger.debug(f"  Output directory: {output_dir}")

    # Create output filename with model (sanitize for filename)
    model_safe = model_name.replace(":", "_").replace("-", "_")
    output_csv = os.path.join(output_dir, f"test_results_form{form_level}_{model_safe}_langchain_agent.csv")
    logger.info(f"  Output CSV: {output_csv}")

    # Validate input files exist
    logger.info(f"\nValidating input files:")
    if not os.path.exists(input_csv):
        logger.error(f"  ✗ Input CSV not found: {input_csv}")
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")
    logger.info(f"  ✓ Input CSV exists")

    if not os.path.exists(img_folder):
        logger.error(f"  ✗ Image folder not found: {img_folder}")
        raise FileNotFoundError(f"Image folder not found: {img_folder}")
    logger.info(f"  ✓ Image folder exists")

    # Count images in folder
    try:
        image_count = len([f for f in os.listdir(img_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))])
        logger.info(f"  ✓ Found {image_count} images in folder")
    except Exception as e:
        logger.warning(f"  Could not count images: {str(e)}")

    # Ensure output directory exists
    logger.info(f"\nCreating output directory:")
    try:
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"  ✓ Output directory ready: {output_dir}")
    except Exception as e:
        logger.error(f"  ✗ Failed to create output directory: {str(e)}")
        raise

    logger.info(f"\n{'='*80}")
    logger.info("Configuration complete. Starting image processing...")
    logger.info(f"{'='*80}\n")

    # Process images
    results_df = process_test_images(input_csv, img_folder, output_csv, model_name)

    # Display first few results
    logger.info(f"\nFirst 3 results:")
    display_results = results_df[['image_filename', 'ground_truth', 'status', 'llm_answer']].head(3)
    logger.info(f"\n{display_results.to_string()}")
    print("\nFirst 3 results:")
    print(display_results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test LangChain Math Agent on Form 4/5 problems",
        epilog="""
Model string format: 'provider:model_name'
Examples:
  - google_genai:gemini-2.5-flash-lite (requires GOOGLE_API_KEY)
  - anthropic:claude-3-5-sonnet-20241022 (requires ANTHROPIC_API_KEY)
  - openai:gpt-4o (requires OPENAI_API_KEY)

Set environment variables in .env file or export them before running.
"""
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
        default=None,
        help="LLM model to use as string (e.g., 'google_genai:gemini-2.5-flash-lite'). "
             "If not provided, uses MODEL_NAME env var or default google_genai:gemini-2.5-flash-lite"
    )
    args = parser.parse_args()

    import asyncio
    asyncio.run(main(args.form, args.model))
