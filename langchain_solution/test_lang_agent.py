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
logger.setLevel(logging.DEBUG)

# File handler (DEBUG level - everything)
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.DEBUG)

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
        logger.info(f"CSV loaded successfully. Total rows: {len(df)}")
        logger.debug(f"Columns in CSV: {list(df.columns)}")
    except Exception as e:
        logger.error(f"Failed to read input CSV: {str(e)}", exc_info=True)
        raise

    # Validate required columns
    required_cols = ['image_filename', 'ground_truth', 'marking_scheme']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        logger.error(f"Missing required columns: {missing_cols}")
        raise ValueError(f"Missing required columns: {missing_cols}")
    logger.debug(f"All required columns present: {required_cols}")

    # Add result columns
    logger.debug("Adding result columns to DataFrame")
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

    for idx, row in tqdm(df.iterrows(), total=len(df)):
        img_filename = row['image_filename']
        img_path = os.path.join(img_folder, img_filename)

        logger.info(f"\n{'='*80}")
        logger.info(f"[{idx+1}/{len(df)}] Processing: {img_filename}")
        logger.debug(f"Image path: {img_path}")

        # Check if image exists
        if not os.path.exists(img_path):
            error_msg = f"Image not found at path: {img_path}"
            logger.warning(error_msg)

            # Save error status
            logger.debug(f"Saving error status for row {idx}")
            df.at[idx, 'llm_answer'] = error_msg
            df.at[idx, 'status'] = "ERROR"
            df.at[idx, 'model'] = model_name
            logger.debug(f"Row {idx} status set to ERROR (image not found)")
            failed += 1
            continue

        try:
            # Process image through two-stage pipeline
            logger.info(f"  Stage 1: Extracting structured data from image...")
            logger.info(f"  Stage 2: Solving with mathematical tools...")

            result = agent.process_image(img_path)
            logger.debug(f"Agent.process_image returned: {type(result)}")

            # Validate result structure
            required_keys = ['extracted_data', 'llm_answer', 'tokens_used', 'status', 'model']
            missing_keys = [k for k in required_keys if k not in result]
            if missing_keys:
                logger.warning(f"Result missing keys: {missing_keys}")
            logger.debug(f"Result keys: {list(result.keys())}")

            # Store results with detailed logging
            logger.debug(f"Storing results in DataFrame at row {idx}...")

            # Log extracted data (truncated if very long)
            extracted_preview = str(result['extracted_data'])[:200]
            logger.debug(f"  extracted_data (first 200 chars): {extracted_preview}...")
            df.at[idx, 'extracted_data'] = result['extracted_data']
            logger.debug(f"  ✓ extracted_data saved")

            # Log answer (truncated if very long)
            answer_preview = str(result['llm_answer'])[:200]
            logger.debug(f"  llm_answer (first 200 chars): {answer_preview}...")
            df.at[idx, 'llm_answer'] = result['llm_answer']
            logger.debug(f"  ✓ llm_answer saved")

            # Log tokens
            tokens = result['tokens_used']
            logger.debug(f"  tokens_used: {tokens}")
            df.at[idx, 'tokens_used'] = tokens
            logger.debug(f"  ✓ tokens_used saved")

            # Log status
            status = result['status']
            logger.debug(f"  status: {status}")
            df.at[idx, 'status'] = status
            logger.debug(f"  ✓ status saved")

            # Log model
            result_model = result['model']
            logger.debug(f"  model: {result_model}")
            df.at[idx, 'model'] = result_model
            logger.debug(f"  ✓ model saved")

            total_tokens += tokens

            # Track success/failure
            if status == "SUCCESS":
                successful += 1
                logger.info(f"  ✓ SUCCESS | Tokens: {tokens} | Running total: {total_tokens}")
            else:
                failed += 1
                logger.warning(f"  ✗ ERROR | Tokens: {tokens} | Running total: {total_tokens}")
                logger.warning(f"  Error details: {result['llm_answer'][:300]}")

        except Exception as e:
            error_msg = f"Exception during image processing: {str(e)}"
            logger.error(error_msg, exc_info=True)

            # Save exception details
            logger.debug(f"Saving exception details for row {idx}")
            df.at[idx, 'llm_answer'] = f"Exception: {str(e)}"
            df.at[idx, 'status'] = "ERROR"
            df.at[idx, 'model'] = model_name
            logger.debug(f"Row {idx} status set to ERROR (exception)")
            failed += 1

    # Save results to CSV
    logger.info(f"\n{'='*80}")
    logger.info(f"Saving results to CSV: {output_csv}")
    try:
        os.makedirs(os.path.dirname(output_csv) if os.path.dirname(output_csv) else '.', exist_ok=True)
        logger.debug(f"Output directory created/verified")

        df.to_csv(output_csv, index=False)
        logger.info(f"✓ Results saved successfully to: {output_csv}")
        logger.debug(f"CSV file size: {os.path.getsize(output_csv)} bytes")
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
