# LangChain Model String Support & Gemini Setup

## Quick Summary

You can now use **any LangChain-supported model** by specifying it as a simple string in the format:
```
"provider:model_name"
```

This works with both the `MathAgent` class and the `test_lang_agent.py` script. Environment variables are automatically loaded from `.env` file.

---

## What Changed

### 1. agent.py (agent_n_tools/)
- ✅ Added `from dotenv import load_dotenv` + `load_dotenv()` call
- ✅ Changed default model to: `"google_genai:gemini-2.5-flash-lite"`
- ✅ Updated docstring to show supported model formats
- ✅ Still works with string-based model specification

### 2. test_lang_agent.py
- ✅ Added `from dotenv import load_dotenv` + `load_dotenv()` call
- ✅ Fixed import to use relative import: `from agent import MathAgent`
- ✅ Updated `main()` to accept `model_name` parameter
- ✅ Added logic to use `MODEL_NAME` env var if available
- ✅ Updated argument parser with better help text and examples
- ✅ Sanitizes model name for output filename

### 3. .env.example (new file)
- Template for setting up your environment variables
- Shows all supported models
- Copy to `.env` and fill in your API keys

---

## Model String Formats

### LangChain v1.0 String Format
```
"provider:model_identifier"
```

**Supported Providers & Models:**

#### Google Gemini
```python
"google_genai:gemini-2.5-flash"          # Fastest, latest
"google_genai:gemini-2.5-flash-lite"     # Smaller, cheaper
"google_genai:gemini-1.5-pro"            # More powerful
"google_genai:gemini-2.0-flex"           # Experimental
```

#### Anthropic Claude
```python
"anthropic:claude-3-5-sonnet-20241022"   # Recommended
"anthropic:claude-opus-4-1"              # More powerful
"anthropic:claude-3-haiku-20250108"      # Faster, cheaper
```

#### OpenAI GPT
```python
"openai:gpt-4o"                          # Most capable
"openai:gpt-4o-mini"                     # Faster, cheaper
"openai:gpt-5"                           # Future model
```

---

## Gemini Setup (Step by Step)

### 1. Get API Key
- Go to [Google AI Studio](https://aistudio.google.com/)
- Click "Get API Key"
- Create new API key
- Copy the key

### 2. Install Required Package
```bash
uv add langchain-google-genai
```

Or:
```bash
pip install -U langchain-google-genai
```

### 3. Create `.env` File
Copy `.env.example` to `.env`:
```bash
cp langchain_solution/.env.example langchain_solution/.env
```

Edit `.env` and add your key:
```
GOOGLE_API_KEY=your-api-key-here
MODEL_NAME=google_genai:gemini-2.5-flash-lite
```

### 4. Use in Code
```python
from agent_n_tools import MathAgent

# Environment variables are loaded automatically
agent = MathAgent()  # Uses MODEL_NAME from .env or default

# Or specify explicitly
agent = MathAgent(model="google_genai:gemini-2.5-flash-lite")
```

### 5. Run Test Script
```bash
cd langchain_solution

# Uses default model from .env
python test_lang_agent.py --form 4

# Or specify model explicitly
python test_lang_agent.py --form 4 --model "google_genai:gemini-2.5-flash-lite"

# Or use different model
python test_lang_agent.py --form 5 --model "anthropic:claude-3-5-sonnet-20241022"
```

---

## Environment Variable Setup

### Option 1: .env File (Recommended for POC)
1. Create `.env` in `langchain_solution/` directory
2. Add your API keys and MODEL_NAME
3. The `load_dotenv()` call loads automatically

### Option 2: Export Environment Variables
```bash
export GOOGLE_API_KEY="your-key-here"
export MODEL_NAME="google_genai:gemini-2.5-flash-lite"
python test_lang_agent.py --form 4
```

### Option 3: Command Line Argument
```bash
python test_lang_agent.py --form 4 --model "anthropic:claude-3-5-sonnet-20241022"
```

**Priority (highest to lowest):**
1. Command-line `--model` argument
2. Environment variable `MODEL_NAME`
3. Default: `google_genai:gemini-2.5-flash-lite`

---

## API Key Requirements by Provider

| Provider | Variable | Where to Get |
|----------|----------|--------------|
| **Google Gemini** | `GOOGLE_API_KEY` | [Google AI Studio](https://aistudio.google.com/) |
| **Anthropic** | `ANTHROPIC_API_KEY` | [Anthropic Console](https://console.anthropic.com/) |
| **OpenAI** | `OPENAI_API_KEY` | [OpenAI Platform](https://platform.openai.com/) |
| **Azure** | `AZURE_OPENAI_API_KEY` | Azure Portal |
| **AWS Bedrock** | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | AWS Console |

---

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'langchain_google_genai'"
**Solution:** Install the Google package
```bash
uv add langchain-google-genai
```

### Issue: "Error: GOOGLE_API_KEY not found"
**Solution:** Make sure .env file exists and contains `GOOGLE_API_KEY=your-key`
```bash
# Check if .env exists
ls -la langchain_solution/.env

# If not, create it
cp langchain_solution/.env.example langchain_solution/.env
# Then edit with your API key
```

### Issue: "load_dotenv() not working"
**Solution:** Make sure you're calling it at the top of your script
```python
from dotenv import load_dotenv
load_dotenv()  # Must be called before importing MathAgent
```

### Issue: Agent uses wrong model
**Solution:** Check the priority order:
1. Did you pass `--model` argument to script?
2. Did you set `MODEL_NAME` in .env?
3. Check if the default model string is correct

---

## Testing the Setup

### Quick Test
```python
from dotenv import load_dotenv
from agent_n_tools import MathAgent

load_dotenv()

# Test with Gemini
agent = MathAgent(model="google_genai:gemini-2.5-flash-lite")
result = agent.solve("Solve 2x + 5 = 15")
print(result)

# Test with Anthropic
agent = MathAgent(model="anthropic:claude-3-5-sonnet-20241022")
result = agent.solve("Calculate the mean of [1, 2, 3, 4, 5]")
print(result)
```

### Test with Script
```bash
# Test Form 4 with Gemini
python test_lang_agent.py --form 4 --model "google_genai:gemini-2.5-flash-lite"

# Test Form 5 with Claude
python test_lang_agent.py --form 5 --model "anthropic:claude-3-5-sonnet-20241022"
```

---

## Model Comparison for Your Use Case

| Model | Cost | Speed | Quality | Vision | Context |
|-------|------|-------|---------|--------|---------|
| **Gemini 2.5 Flash Lite** | $ | ⚡⚡⚡ | ⭐⭐⭐ | ✅ | 1M |
| **Gemini 2.5 Flash** | $$ | ⚡⚡ | ⭐⭐⭐⭐ | ✅ | 1M |
| **Claude 3.5 Sonnet** | $$$ | ⚡ | ⭐⭐⭐⭐⭐ | ✅ | 200K |
| **GPT-4o** | $$$ | ⚡ | ⭐⭐⭐⭐⭐ | ✅ | 128K |

**Recommendation for POC:** Start with `gemini-2.5-flash-lite` (cheapest, fastest), then compare results with Claude and GPT if needed.

---

## Files Updated/Created

```
langchain_solution/
├── .env.example                      # NEW: Template for env vars
├── MODEL_STRING_GUIDE.md             # NEW: Detailed model string docs
├── GEMINI_AND_MODEL_SETUP.md         # NEW: This file
├── agent_n_tools/
│   └── agent.py                      # UPDATED: load_dotenv, model string docs
└── test_lang_agent.py                # UPDATED: load_dotenv, arg parsing, env vars
```

---

## Next Steps

1. **Install dependencies:**
   ```bash
   uv add python-dotenv langchain-google-genai
   ```

2. **Create .env file:**
   ```bash
   cp langchain_solution/.env.example langchain_solution/.env
   # Edit with your API keys
   ```

3. **Test the agent:**
   ```bash
   python langchain_solution/test_lang_agent.py --form 4
   ```

4. **Compare models** (optional):
   ```bash
   python langchain_solution/test_lang_agent.py --form 4 --model "google_genai:gemini-2.5-flash-lite"
   python langchain_solution/test_lang_agent.py --form 4 --model "anthropic:claude-3-5-sonnet-20241022"
   ```

---

## Key Takeaway

With LangChain v1.0's string-based model specification:
- ✅ No need to import specific model classes
- ✅ Easy to swap between providers
- ✅ Environment variables loaded automatically
- ✅ Works seamlessly with `create_agent()`

Your code is now provider-agnostic and flexible! 🎉
