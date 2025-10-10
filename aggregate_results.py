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

    # Remove summary rows (rows with NaN filename or filename containing 'total')
    df4 = df4.dropna(subset=['filename'])
    df5 = df5.dropna(subset=['filename'])
    df4 = df4[~df4['filename'].str.contains('total', case=False, na=False)]
    df5 = df5[~df5['filename'].str.contains('total', case=False, na=False)]

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
            'form4': r'QAs\gemini-2.5-flash-lite-preview-09-2025\test_results_form4_gemini-2.5-flash-lite-preview-09-2025_COT+StepBack_evaluation_result_2025-10-10_11-03-14.xlsx',
            'form5': r'QAs\gemini-2.5-flash-lite-preview-09-2025\test_results_form5_gemini-2.5-flash-lite-preview-09-2025_COT+StepBack_evaluation_result_2025-10-10_11-01-15.xlsx',
            'method': 'gemini-2.5-flash-lite-preview-09-2025_COT+StepBack'
        },
        {
            'form4': r'QAs\result\test_results_f4_evaluation_result_2025-10-07_22-57-47.xlsx',
            'form5': r'QAs\result\test_results_f5_evaluation_result_2025-10-07_23-24-07.xlsx',
            'method': 'gemini-2.0-flash'
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
    output_path = 'QAs/evaluation_summary_gemini.xlsx'
    summary_df.to_excel(output_path, index=False)

    print(f"Summary saved to {output_path}")
    print("\nSummary:")
    print(summary_df.to_string(index=False))


if __name__ == '__main__':
    main()
