# LangChain Model String Specification Guide

## Overview
LangChain v1.0+ supports specifying models as simple strings in the format:
```
"provider:model_name"
```

This works with `create_agent()` and allows automatic provider detection without needing to instantiate model classes directly.

## Supported Model Strings

### Anthropic
```python
model = "anthropic:claude-3-5-sonnet-20241022"
model = "anthropic:claude-opus-4-1"
model = "anthropic:claude-sonnet-4-5"
```

### OpenAI
```python
model = "openai:gpt-4o"
model = "openai:gpt-4o-mini"
model = "openai:gpt-5"
```

### Google Gemini (ChatGoogleGenerativeAI)
```python
model = "google_genai:gemini-2.5-flash"
model = "google_genai:gemini-2.5-flash-lite"
model = "google_genai:gemini-1.5-pro"
model = "google_genai:gemini-2.0-flex"
```

### Azure OpenAI
```python
model = "azure-openai:gpt-4"
```

### AWS Bedrock
```python
model = "bedrock:claude-3-sonnet-20240229-v1:0"
```

## Using Model Strings with create_agent()

```python
from langchain.agents import create_agent

# Simply pass the string
agent = create_agent(
    model="google_genai:gemini-2.5-flash-lite",
    tools=[my_tool],
    system_prompt="You are helpful"
)

# Or with Anthropic
agent = create_agent(
    model="anthropic:claude-3-5-sonnet-20241022",
    tools=[my_tool],
    system_prompt="You are helpful"
)
```

## Gemini Setup

### Step 1: Install Package
```bash
uv add langchain-google-genai
```

Or:
```bash
pip install -U langchain-google-genai
```

### Step 2: Set Environment Variable
```bash
export GOOGLE_API_KEY="your-api-key-here"
```

Or in `.env` file:
```
GOOGLE_API_KEY=your-api-key-here
```

### Step 3: Load in Python
```python
from dotenv import load_dotenv
import os

load_dotenv()  # Loads GOOGLE_API_KEY from .env

# Now use the string-based model
model = "google_genai:gemini-2.5-flash-lite"
```

### Step 4: Use with create_agent()
```python
from langchain.agents import create_agent

agent = create_agent(
    model="google_genai:gemini-2.5-flash-lite",
    tools=my_tools,
    system_prompt="Your prompt here"
)
```

## Comparison: String vs Class Instantiation

### String Approach (Recommended for POC)
```python
from langchain.agents import create_agent

agent = create_agent(
    model="google_genai:gemini-2.5-flash-lite",
    tools=my_tools
)
```

### Class Approach (More Control)
```python
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0.7
)

agent = create_agent(
    model=llm,
    tools=my_tools
)
```

## Available Gemini Models

| Model | Description | Context |
|-------|-------------|---------|
| `gemini-2.5-flash` | Latest, fastest Gemini | 1M tokens |
| `gemini-2.5-flash-lite` | Smaller, cheaper Gemini | 1M tokens |
| `gemini-1.5-pro` | Previous powerful model | 1M tokens |
| `gemini-2.0-flex` | Experimental model | Varies |

## Required Environment Variables by Provider

| Provider | Variable | Example |
|----------|----------|---------|
| Anthropic | `ANTHROPIC_API_KEY` | Set by default if using langchain-anthropic |
| OpenAI | `OPENAI_API_KEY` | Your OpenAI API key |
| Google Gemini | `GOOGLE_API_KEY` | Your Google AI Studio key |
| Azure | `AZURE_OPENAI_API_KEY` | Your Azure key |
| AWS | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | AWS credentials |

## Using load_dotenv()

```python
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Now all environment variables from .env are accessible
api_key = os.getenv("GOOGLE_API_KEY")
model_name = os.getenv("MODEL_NAME", "google_genai:gemini-2.5-flash-lite")
```

Create `.env` file in project root:
```
GOOGLE_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
MODEL_NAME=google_genai:gemini-2.5-flash-lite
```

## Notes for Your Math Agent

- Your agent can accept model string as parameter: `agent = MathAgent(model="google_genai:gemini-2.5-flash-lite")`
- The `create_agent()` function will automatically detect the provider from the string
- No need to import `ChatGoogleGenerativeAI` unless you need custom configuration
- For POC, string-based approach is simpler and sufficient
