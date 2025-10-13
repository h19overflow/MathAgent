"""
python run_ace_test.py --form 4
python run_ace_test.py --form 5
python run_ace_test.py --form 4 --shared-context --llm-feedback --correctness-check
"""

import argparse
import os
import asyncio
import logging
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from pydantic_ai import Agent

from ace.models import Context
from ace.orchestrator import initialize_context, run_ace_pipeline

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are an expert mathematician. Analyze the provided image and question to arrive at a solution. Follow these steps precisely in your response:
Step 1: Diagram Deconstruction.
Identify the type of mathematical diagram (e.g., 'Linear inequality graph,' 'Venn diagram,' 'Histogram').
Extract all key features directly from the diagram. For a graph, list the equations of the lines, intercepts, and labeled points. For a chart, extract the data points. For a network, list the nodes and edges with their weights.
Step 2: Question Interpretation.
State the explicit goal of the question. What specific value or statement needs to be produced?
Step 3: Mathematical Formulation.
Based on the deconstructed diagram from Step 1 and the question from Step 2, formulate the necessary mathematical equations, inequalities, or logical statements.
Step 4: Step-by-Step Calculation.
Solve the formulation from Step 3. Show every step of your calculation.
Step 5: Final Answer.
State the final answer clearly, ensuring it directly addresses the question.
"""

USER_PROMPT = "Solve the following question i want you to first analayze the questions then start solving make sure your answer is complete, dont answer in markdown"


def initialize_agent(model_name: str) -> Agent:
    return Agent(model_name, system_prompt=SYSTEM_PROMPT)


async def get_answer_with_ace(
    agent: Agent,
    context: Context,
    image_path: str,
    ground_truth: str,
    use_llm_feedback: bool = False,
    use_correctness_check: bool = False
) -> tuple[str, int, Context]:
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()

        answer, updated_context, tokens = await run_ace_pipeline(
            agent,
            context,
            USER_PROMPT,
            image_data,
            ground_truth,
            refinement_mode="eager",
            use_llm_feedback=use_llm_feedback,
            use_correctness_check=use_correctness_check,
            max_context_size=20
        )

        return answer, tokens, updated_context
    except Exception as e:
        logger.error(f"Error processing {image_path}: {e}", exc_info=True)
        return f"Error: {e}", 0, context


async def process_test_images(
    input_csv: str,
    img_folder: str,
    output_csv: str,
    model_name: str,
    use_shared_context: bool = False,
    use_llm_feedback: bool = False,
    use_correctness_check: bool = False
):
    """Process the test images with the ACE framework."""
    print(f"Reading CSV from {input_csv}...")
    df = pd.read_csv(input_csv)

    required_cols = ['image_filename', 'ground_truth', 'marking_scheme']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    df['llm_answer'] = ""
    df['tokens_used'] = 0
    df['status'] = ""
    df['model'] = ""

    agent = initialize_agent(model_name)
    shared_context = initialize_context() if use_shared_context else None
    total_tokens = 0

    mode = "SHARED" if use_shared_context else "ISOLATED"
    features = []
    if use_llm_feedback:
        features.append("LLM-Feedback")
    if use_correctness_check:
        features.append("Correctness-Check")
    feature_str = f" | Features: {', '.join(features)}" if features else ""

    print(f"\nProcessing {len(df)} images (Mode: {mode}{feature_str})...")

    for idx, row in tqdm(df.iterrows(), total=len(df)):
        img_filename = row['image_filename']
        img_path = os.path.join(img_folder, img_filename)
        ground_truth = row['ground_truth']

        if not os.path.exists(img_path):
            print(f"\nWarning: Image not found: {img_path}")
            df.at[idx, 'llm_answer'] = "Image not found"
            df.at[idx, 'status'] = "ERROR"
            df.at[idx, 'model'] = model_name
            continue

        print(f"\nProcessing: {img_filename}")

        context = shared_context if use_shared_context else initialize_context()
        answer, tokens, context = await get_answer_with_ace(
            agent, context, img_path, ground_truth, use_llm_feedback, use_correctness_check
        )

        if use_shared_context:
            shared_context = context

        df.at[idx, 'llm_answer'] = answer
        df.at[idx, 'tokens_used'] = tokens
        df.at[idx, 'status'] = "SUCCESS" if not answer.startswith("Error") else "ERROR"
        df.at[idx, 'model'] = model_name

        total_tokens += tokens
        print(f"Tokens used: {tokens} | Total so far: {total_tokens}")
        print(f"Context size: {len(context.bullets)} bullets")

    print(f"\nSaving results to {output_csv}...")
    df.to_csv(output_csv, index=False)

    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total images processed: {len(df)}")
    print(f"Successful: {len(df[df['status'] == 'SUCCESS'])}")
    print(f"Errors: {len(df[df['status'] == 'ERROR'])}")
    print(f"Total tokens used: {total_tokens}")
    print(f"Final context size: {len(context.bullets)} bullets")
    print(f"Results saved to: {output_csv}")
    print("="*60)

    return df


async def main(
    form_level: str,
    use_shared_context: bool = False,
    use_llm_feedback: bool = False,
    use_correctness_check: bool = False
):
    base_dir = r"C:\Users\Adonis\OneDrive\Desktop\DataScience\evaluation\QAs"

    input_csv = os.path.join(base_dir, f"test_questions_mathform{form_level}.csv")
    img_folder = os.path.join(base_dir, "Soalan maths", f"form {form_level}")
    output_csv = os.path.join(base_dir, "ace-results", f"answering_results_enhanced{form_level}_ace.csv")
    model_name = "gemini-2.5-flash-lite-preview-09-2025"

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")
    if not os.path.exists(img_folder):
        raise FileNotFoundError(f"Image folder not found: {img_folder}")

    results_df = await process_test_images(
        input_csv,
        img_folder,
        output_csv,
        model_name,
        use_shared_context,
        use_llm_feedback,
        use_correctness_check
    )

    print("\nFirst 3 results:")
    print(results_df[['image_filename', 'ground_truth', 'llm_answer', 'status']].head(3))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--form", type=str, required=True, choices=["4", "5"], help="Form level: 4 or 5")
    parser.add_argument("--shared-context", action="store_true", help="Use shared context across all images (default: isolated)")
    parser.add_argument("--llm-feedback", action="store_true", help="Use LLM-based bullet feedback evaluation")
    parser.add_argument("--correctness-check", action="store_true", help="Use correctness-aware reflection")

    args = parser.parse_args()
    asyncio.run(main(args.form, args.shared_context, args.llm_feedback, args.correctness_check))
