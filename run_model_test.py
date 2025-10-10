import argparse
import os
import asyncio
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from pydantic_ai import Agent, BinaryContent
# TODO , run the gpt-5-mini model, on form 4 and form 5 , ensure that the output csv is saved in the gpt-5-mini folder, analyze the output and make sure to note down the difference
load_dotenv()

SYSTEM_PROMPT = """
You are an expert mathematician. Before analyzing the image, begin with a principle-first approach to ensure accurate reasoning. Follow these steps precisely:

Step 0: Principle Abstraction
Identify the general mathematical concept involved, independent of the image. Ask: “What high-level principle, law, or category applies to this problem?” Examples include: “system of linear inequalities,” “quadratic optimization,” “conditional probability,” or “triangle congruence.” Do not reference visual elements yet.

Step 1: Diagram Deconstruction
Now, analyze the provided image. Identify the type of mathematical diagram (e.g., 'Linear inequality graph,' 'Venn diagram,' 'Histogram'). Extract all key features: for graphs, list equations of lines, intercepts, and labeled points; for charts, extract data points; for networks, list nodes, edges, and weights. Ensure all extracted elements align with the principle identified in Step 0.

Step 2: Question Interpretation
State the explicit goal of the question. What specific value, expression, or statement is required? Link it to the abstracted principle and diagram features.

Step 3: Mathematical Formulation
Using the principle from Step 0 and the extracted features from Step 1, formulate the necessary equations, inequalities, or logical statements. Ensure consistency between the high-level concept and the specific instance.

Step 4: Step-by-Step Calculation
Solve the formulation from Step 3. Show every computational or logical step. For numerical operations, use exact arithmetic or symbolic simplification.

Step 5: Final Answer
State the final answer clearly, ensuring it directly addresses the question. Box the result if applicable.
"""

USER_PROMPT = "Solve the following question i want you to first analayze the questions then start solving make sure your answer is complete, dont answer in markdown"


def initialize_agent(model_name: str) -> Agent:
    return Agent(model_name, system_prompt=SYSTEM_PROMPT)

async def get_answer_from_image(agent: Agent, image_path: str) -> tuple[str, int]:
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()

        result = await agent.run([
            USER_PROMPT,
            BinaryContent(data=image_data, media_type='image/png'),
        ])

        answer = result.output
        tokens = 0

        # Correct way: Call .usage() method
        if hasattr(result, 'usage'):
            usage = result.usage()  # This returns RunUsage(input_tokens=int, output_tokens=int, requests=int)
            tokens = usage.input_tokens + usage.output_tokens

        return answer, tokens

    except Exception as e:
        return f"Error: {e}", 0


async def process_test_images(input_csv: str, img_folder: str, output_csv: str, model_name: str):
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
    total_tokens = 0

    print(f"\nProcessing {len(df)} images...")
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

        answer, tokens = await get_answer_from_image(agent, img_path)

        df.at[idx, 'llm_answer'] = answer
        df.at[idx, 'tokens_used'] = tokens
        df.at[idx, 'status'] = "SUCCESS" if not answer.startswith("Error") else "ERROR"
        df.at[idx, 'model'] = model_name

        total_tokens += tokens
        print(f"Tokens used: {tokens} | Total so far: {total_tokens}")

    print(f"\nSaving results to {output_csv}...")
    df.to_csv(output_csv, index=False)

    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total images processed: {len(df)}")
    print(f"Successful: {len(df[df['status'] == 'SUCCESS'])}")
    print(f"Errors: {len(df[df['status'] == 'ERROR'])}")
    print(f"Total tokens used: {total_tokens}")
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