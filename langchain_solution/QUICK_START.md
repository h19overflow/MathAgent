# Quick Start Guide - LangChain Math Agent with Gemini

## 5-Minute Setup

### 1. Install Dependencies
```bash
cd langchain_solution
uv add python-dotenv langchain-google-genai
```

### 2. Get Gemini API Key
- Go to [Google AI Studio](https://aistudio.google.com/apikey)
- Create API key
- Copy the key

### 3. Create .env File
```bash
cp .env.example .env
```

Edit `.env`:
```
GOOGLE_API_KEY=paste-your-key-here
MODEL_NAME=google_genai:gemini-2.5-flash-lite
```

### 4. Test It
```bash
python test_lang_agent.py --form 4
```

Done! ✅

---

## Common Commands

### Run Tests
```bash
# Form 4 with Gemini (default)
python test_lang_agent.py --form 4

# Form 5 with Claude instead
python test_lang_agent.py --form 5 --model "anthropic:claude-3-5-sonnet-20241022"

# With help
python test_lang_agent.py --help
```

### Use Agent Directly
```python
from langchain_solution.agent_n_tools import MathAgent

agent = MathAgent(model="google_genai:gemini-2.5-flash-lite")
answer = agent.solve("Solve 2x + 5 = 15")
print(answer)
```

### Process Images
```python
agent = MathAgent()
result = agent.process_image("path/to/math_problem.png")
print(result['llm_answer'])
```

---

## Model Strings

### Fast & Cheap (Recommended for POC)
```
google_genai:gemini-2.5-flash-lite
```

### Best Quality
```
anthropic:claude-3-5-sonnet-20241022
openai:gpt-4o
```

### All Available
See `MODEL_STRING_GUIDE.md` or `GEMINI_AND_MODEL_SETUP.md`

---

## Environment Variables

### Required
- `GOOGLE_API_KEY` - for Gemini models

### Optional
- `MODEL_NAME` - which model to use (default: gemini-2.5-flash-lite)
- `ANTHROPIC_API_KEY` - if using Claude
- `OPENAI_API_KEY` - if using GPT

All set in `.env` file (automatically loaded)

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Module not found | `uv add langchain-google-genai` |
| API key error | Check `.env` file exists and has key |
| Wrong model used | Check `MODEL_NAME` in `.env` or use `--model` arg |
| .env not loading | Make sure it's in `langchain_solution/` folder |

---

## File Locations

```
langchain_solution/
├── .env                    ← Your API keys (create from .env.example)
├── agent_n_tools/
│   └── agent.py           ← MathAgent class
├── test_lang_agent.py     ← Test script
├── GEMINI_AND_MODEL_SETUP.md
├── MODEL_STRING_GUIDE.md
└── QUICK_START.md         ← This file
```

---

## More Info

- **Model Strings**: See `MODEL_STRING_GUIDE.md`
- **Full Setup**: See `GEMINI_AND_MODEL_SETUP.md`
- **Agent Docs**: See `agent_n_tools/README.md`
- **Error Mitigation**: See `../MITIGATION_PLAN.md`

---

Done! You're all set. Run `python test_lang_agent.py --form 4` to start testing! 🚀
