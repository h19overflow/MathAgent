pyth# Branch for evaluating the QA on image

## Input file
Use test_results_f4.csv as templates
make sure the alocated mark for each questions is in the marking_scheme column

## 

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


## Output File
Evaluation file will be outputted in the same folder as the llm_answer_evaluation script
## Command to run script
```
python llm_answer_evaluation.py --input_file "path_to_file.csv"
```
