pyth# Similarity and Marking Evaluation script

Branch for evaluating the similarity between the ground truth answers and AI/LLM answers.
Also perform marking on the AI answers using LLM.

## Requirements
- argparse
- datetime
- os
- pandas
- langchain_openai
- langchain_core
- time
- json

If the above libraries are installed, no need to ```pip install -r requirements.txt```

## Input File
The test dataset should have these requirements:
- 'question' column
- 'answer' column
- 'llm_answer' column
- .csv, .xls or .xlsx extension

## Output File
Evaluation file will be outputted in the same folder as the llm_answer_evaluation script
## Command to run script
```
python llm_answer_evaluation.py --input_file "path_to_file.csv"
```
