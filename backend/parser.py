# parser.py — LLM Response Parsing Module
# Claude returns plain text. This module splits that text into three categories:
# bugs, security vulnerabilities, and quality suggestions.

import re
from typing import Dict, List


def parse_response(raw_text: str) -> Dict[str, List[str]]:
    """
    Parses raw Claude feedback into structured categories.

    Args:
        raw_text (str): The raw text string returned by Claude.

    Returns:
        dict: A dictionary with keys 'bugs', 'security', 'quality'.
              Each value is a list of strings (the individual findings).
              Returns empty lists if a section is missing or says 'None identified.'

    Example output:
        {
            "bugs": ["Missing null check on line 5"],
            "security": [],
            "quality": ["Add type hints to function parameters"]
        }
    """
    result = {'bugs': [], 'security': [], 'quality': []}

    section_patterns = {
        'bugs':     r'BUGS:\s*(.*?)(?=SECURITY:|QUALITY:|$)',
        'security': r'SECURITY:\s*(.*?)(?=BUGS:|QUALITY:|$)',
        'quality':  r'QUALITY:\s*(.*?)(?=BUGS:|SECURITY:|$)',
    }

    for key, pattern in section_patterns.items():
        match = re.search(pattern, raw_text, re.DOTALL | re.IGNORECASE)
        if match:
            section_text = match.group(1).strip()

            if section_text.lower().startswith('none identified'):
                continue

            items = [
                line.strip().lstrip('-*• ').strip()
                for line in section_text.split('\n')
                if line.strip() and line.strip() not in ['-', '*', '•']
            ]

            result[key] = [item for item in items if item]

    return result