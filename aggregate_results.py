"""
Aggregate evaluation results from multiple Excel files.

Reads Excel files containing model evaluation results and creates a summary
with total marks, accuracy percentage, and token usage per method.
"""

import pandas as pd
from pathlib import Path


def aggregate_file_pair(form4_path: str, form5_path: str, method_name: str) -> dict:
    """
    Aggregate results from a pair of Form 4 and Form 5 files.

    Args:
        form4_path: Path to Form 4 Excel file
        form5_path: Path to Form 5 Excel file
        method_name: Name of the method/approach

    Returns:
        Dictionary with aggregated results
    """
    df4 = pd.read_excel(form4_path)
    df5 = pd.read_excel(form5_path)

    # Remove summary rows (rows with NaN filename)
    df4 = df4.dropna(subset=['filename'])
    df5 = df5.dropna(subset=['filename'])

    # Combine both forms
    combined = pd.concat([df4, df5], ignore_index=True)

    # Calculate aggregates
    total_ai_marks = combined['ai_marks'].sum()
    total_allocated_marks = combined['allocated_marks'].sum()
    accuracy = (total_ai_marks / total_allocated_marks * 100) if total_allocated_marks > 0 else 0
    total_tokens = combined['token_used'].sum()
    model_used = combined['model_used'].iloc[0]

    return {
        'method': method_name,
        'model_used': model_used,
        'total_ai_marks': total_ai_marks,
        'total_allocated_marks': total_allocated_marks,
        'accuracy_percentage': round(accuracy, 2),
        'total_tokens_used': total_tokens
    }


def main():
    """Create summary Excel from evaluation results."""

    # Define file pairs
    file_pairs = [
        {
            'form4': 'QAs/gpt-5-mini_COT+StepBack/test_results_form4_gpt-5-mini_COT+StepBack_evaluation_result_2025-10-10_10-02-06.xlsx',
            'form5': 'QAs/gpt-5-mini_COT+StepBack/test_results_form5_gpt-5-mini_COT+StepBack_evaluation_result_2025-10-10_10-20-16.xlsx',
            'method': 'gpt-5-mini_COT+StepBack'
        },
        {
            'form4': 'QAs/result/test_results_f4_gpt5mini_evaluation_result_2025-10-07_21-02-53.xlsx',
            'form5': 'QAs/result/test_results_f5_gpt5mini_evaluation_result_2025-10-07_21-47-28.xlsx',
            'method': 'gpt5mini_baseline'
        }
    ]

    # Aggregate results
    results = []
    for pair in file_pairs:
        result = aggregate_file_pair(pair['form4'], pair['form5'], pair['method'])
        results.append(result)

    # Create summary DataFrame
    summary_df = pd.DataFrame(results)

    # Reorder columns
    summary_df = summary_df[['method', 'model_used', 'total_ai_marks',
                             'total_allocated_marks', 'accuracy_percentage',
                             'total_tokens_used']]

    # Save to Excel
    output_path = 'QAs/evaluation_summary.xlsx'
    summary_df.to_excel(output_path, index=False)

    print(f"Summary saved to {output_path}")
    print("\nSummary:")
    print(summary_df.to_string(index=False))


if __name__ == '__main__':
    main()
