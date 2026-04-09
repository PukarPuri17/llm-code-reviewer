# reviewer.py — LLM API Integration Module
# This module handles all communication with the Anthropic Claude API.
# It builds the prompt and sends it to Claude, then returns the raw response.

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()  # Loads your API key from the .env file (never hardcode keys!)

# Prompt template — the structure here is critical.
# We force Claude to respond in exactly three labeled sections so parser.py can split it reliably.
PROMPT_TEMPLATE = """You are a senior software engineer reviewing code for quality and security.

Analyze the following {language} code and provide feedback in exactly three sections:

BUGS: List any logical errors or incorrect behavior. Use bullet points.
SECURITY: List any security vulnerabilities. Use bullet points.
QUALITY: List code quality improvements. Use bullet points.

If a section has no issues, write exactly: None identified.

Code:
{code}
"""

def build_prompt(code: str, language: str) -> str:
    """
    Constructs a structured prompt for Claude.

    Args:
        code (str): The source code to be reviewed.
        language (str): Programming language of the code (e.g. 'python', 'javascript').

    Returns:
        str: Fully formatted prompt string ready to send to the API.
    """
    return PROMPT_TEMPLATE.format(language=language, code=code)


def call_llm_api(prompt: str) -> str:
    """
    Sends the prompt to the Anthropic Claude API and returns the raw text response.

    Args:
        prompt (str): The fully constructed prompt string.

    Returns:
        str: Raw text response from Claude.

    Raises:
        RuntimeError: If the API call fails for any reason (timeout, auth error, etc.)
    """
    try:
        client = anthropic.Anthropic(api_key=os.getenv("LLM_API_KEY"))

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",  # Fast and cost-effective
            max_tokens=1024,                     # Cap response length to control cost
            temperature=0.2,                     # Low temperature = more consistent output
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return message.content[0].text

    except anthropic.AuthenticationError:
        raise RuntimeError("Invalid API key. Check your .env file.")
    except anthropic.RateLimitError:
        raise RuntimeError("API rate limit exceeded. Please wait and try again.")
    except anthropic.APITimeoutError:
        raise RuntimeError("API request timed out. Please try again.")
    except Exception as e:
        raise RuntimeError(f"Unexpected API error: {str(e)}")