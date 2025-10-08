QUESTION = "question"
GROUND_TRUTH = "ground_truth"
LLM_ANSWER = "llm_answer"
OPENAI_TOKEN_USAGE = "token_usage"
LLM_CORRECTNESS_PROMPTS = """
You are comparing ground truth answer and AI response from LLM based on the question.
Follow these steps:
1. Asess the similarity in terms of meaning and content between the AI response and the ground truth answer.
2. Respond with 'correct' if the AI response is contextually similar to the ground truth.
3. Respond with 'wrong' if the AI response is not contextually similar to the ground truth.

Here is the question: {question}
Here is the ground truth answer: {ground_truth_answer}
Here is the AI response: {ai_answer}

Respond your evaluation in the following JSON format below:

    [{{
        "similarity": <correct/wrong>
    }}]
"""

LLM_CORRECTNESS_PROMPT = """
You are comparing ground truth answer and AI response from LLM
Follow these steps:
1. Asess the similarity in terms of meaning and content between the AI response and the ground truth answer.
2. Respond with 'correct' if the AI response is contextually similar to the ground truth.
3. Respond with 'wrong' if the AI response is not contextually similar to the ground truth.

Here is the ground truth answer: {ground_truth_answer}
Here is the AI response: {ai_answer}

Respond your evaluation in the following JSON format below:

    [{{
        "similarity": <correct/wrong>
    }}]
"""

LLM_MARKING_PROMPTS = """
You are evaluating an AI model's mathematical problem-solving response using secondary school mathematics teacher standards in Malaysia.
Follow these evaluation criteria:
1. Provide a score based on the mark defined in the ground truth answer schema.
2. Explain your reasoning for the score that you provide.
3. Follow the marking schema provided in the ground truth answer strictly. If its not provided, use default marking schema in Sijil Pelajar Malaysia (SPM).
4. If its a multiple choice type questions, the score is either 1 or 0 for correct and incorrect answer respectively.
5. If its an open ended type questions, the score should follow the marking schema in Sijil Pelajar Malaysia (SPM) usually in whole number.
6. Treat the above conditions as strict rules.

Here is the question: {question}
Here is the ground truth answer: {ground_truth_answer}
Here is the AI response: {ai_answer}

Respond your evaluation in the following JSON format below:

    [{{
        "ai_score": <score>,
        "ai_score_explanation": <explanation>
    }}]
"""

LLM_MARKING_PROMPT = """
You are evaluating an AI model's mathematical problem-solving response using secondary school mathematics teacher standards in Malaysia.
Follow these evaluation criteria:
1. Provide a score based on the mark defined in the ground truth answer schema or default marking schema.
2. Explain your reasoning for the score that you provide.
3. Follow the marking schema provided in the ground truth answer strictly. If its not provided, use default marking schema in Sijil Pelajar Malaysia (SPM).
4. If its a multiple choice type questions, the score is either 1 or 0 for correct and incorrect answer respectively.
5. If its an open ended type questions, the score should follow the marking schema in Sijil Pelajar Malaysia (SPM) usually in whole number.
6. Treat the above conditions as strict rules.

Here is the ground truth answer: {ground_truth_answer}
Here is the AI response: {ai_answer}
Here is the marking scheme: {marking_scheme}

Respond your evaluation in the following JSON format below:

    [{{
        "ai_score": <score>,
        "ai_score_explanation": <explanation>
    }}]
"""