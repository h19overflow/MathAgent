import argparse
from datetime import datetime
import os
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from config import OPENAI_DEPLOYMENT_NAME, OPENAI_API_KEY
from constant import LLM_CORRECTNESS_PROMPT, LLM_MARKING_PROMPT, QUESTION, ANSWER, LLM_ANSWER, OPENAI_TOKEN_USAGE
import time
import json

def initialize_client() -> ChatOpenAI:
    return ChatOpenAI(
        model=OPENAI_DEPLOYMENT_NAME,
        openai_api_key=OPENAI_API_KEY
    )

def process_df(input_file: str):
    """
    Checks if the input file has the required columns
    
    Args:
        input_file (str): Path to the input file.
    Returns:
        pd.DataFrame
    """
    if input_file.endswith(".csv"):
        df = pd.read_csv(input_file)
    elif input_file.endswith(".xlsx") or input_file.endswith(".xls"):
        df = pd.read_excel(input_file)
    else:
        raise ValueError(f"Unsupported file format: {input_file}. Supported formats are .csv, .xls, .xlsx")
    
    df.columns = df.columns.str.lower()
    if all(col in df.columns.str.lower() for col in [QUESTION, ANSWER, LLM_ANSWER]):
        return df
    else:
        raise ValueError(f"Columns {QUESTION}, {ANSWER}, and {LLM_ANSWER} are required in the file.")
    
def correctness_evaluation(client: ChatOpenAI, system_message: SystemMessage, question: str, ground_truth_answer: str, generated_answer: str):
    """
    Evaluates the correctness of LLM answers.

    Args:
        client (ChatOpenAI): OpenAI client.
        system_message (SystemMessage): System message.
        question (str): Question.
        ground_truth_answer (str): Ground truth answer.
        generated_answer (str): Generated LLM answer.

    Returns:
        tuple: Tuple containing the correctness response and token usage.
    """
    correctness_prompt = LLM_CORRECTNESS_PROMPT.format(
        ground_truth_answer=ground_truth_answer, ai_answer=generated_answer, question=question)

    human_message = HumanMessage(
        content=correctness_prompt
    )
    correctness_response = client.invoke([system_message, human_message])
    final_correctness_response = json.loads(correctness_response.content)
    return final_correctness_response, correctness_response.response_metadata[OPENAI_TOKEN_USAGE]

def marking_evaluation(client: ChatOpenAI, system_message: SystemMessage, question: str, ground_truth_answer: str, generated_answer: str):

    """
    Marks the LLM answers using LLM.

    Args:
        client (ChatOpenAI): OpenAI client.
        system_message (SystemMessage): System message.
        question (str): Question.
        ground_truth_answer (str): Ground truth answer.
        generated_answer (str): Generated LLM answer.

    Returns:
        tuple: Tuple containing the marking response and token usage.
    """
    marking_prompt = LLM_MARKING_PROMPT.format(
        question=question, ground_truth_answer=ground_truth_answer, ai_answer=generated_answer
    )

    human_message = HumanMessage(
        content=marking_prompt
    )
    marking_response = client.invoke([system_message, human_message])
    final_marking_response = json.loads(marking_response.content)
    return final_marking_response, marking_response.response_metadata[OPENAI_TOKEN_USAGE]

def llm_evaluation(df: pd.DataFrame):
    """
    Evaluate LLM answers based on correctness and marking.
    Args:
        df (pd.DataFrame): DataFrame containing questions, answers, and LLM answers.
    Returns:
        pd.DataFrame: DataFrame with evaluation results.
    """
    csv_data = []
    client = initialize_client()
    system_message = SystemMessage(
        content="You are an expert evaluator of LLM outputs. Follow the evaluation rules strictly and return JSON only."
    )
    total_correctness_time = 0
    total_marking_time = 0
    try:
        for index, row in df.iterrows():
            question = row[QUESTION]
            ground_truth_answer = row[ANSWER]
            generated_answer = row[LLM_ANSWER]
            
            print(f"Processing row {index+1} out of {len(df)}")
            start_correctness_time = time.time()
            correctness_response, correctness_usage = correctness_evaluation(client, system_message, question, ground_truth_answer, generated_answer)
            correctness_time = time.time() - start_correctness_time

            start_marking_time = time.time()
            marking_response, marking_usage = marking_evaluation(client, system_message, question, ground_truth_answer, generated_answer)
            marking_time = time.time() - start_marking_time

            total_correctness_time += correctness_time
            total_marking_time += marking_time

            if correctness_response and marking_response:
                csv_data.append({
                    QUESTION: question,
                    "ground_truth_answer": ground_truth_answer,
                    "generated_answer": generated_answer,
                    "similarity": correctness_response[0]["similarity"],
                    "correctness_time": correctness_time,
                    "ai_marks": marking_response[0]["ai_score"],
                    "marking_explanation": marking_response[0]["ai_score_explanation"],
                    "marking_time": marking_time
                })
        print(f"Evaluation completed for {len(df)} rows.")
    except Exception as e:
        print(f"Error processing row {index}: {e} \n Correctness Evaluation: {correctness_response} \n Marking Evaluation: {marking_response}")

    
    print(f"Total Correctness Time: {total_correctness_time}s")
    print(f"Total Marking Time: {total_marking_time}s")
    return pd.DataFrame(csv_data)

def main(input_file: str):
    """
    Main function to process the input file and evaluate LLM answers.
    Command to run: 
    python llm_answer_evaluation.py --input_file <input_file_path>
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"File not found: {input_file}")
    
    print(f"Processing file: {input_file}")
    
    df = process_df(input_file)
    result = llm_evaluation(df)

    filename = os.path.splitext(os.path.basename(input_file))[0]
    result.to_csv(f"{filename}_evaluation_result_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str, required=True, help="Path to the input file containing questions, answers, and LLM answers.")

    args = parser.parse_args()
    main(args.input_file)