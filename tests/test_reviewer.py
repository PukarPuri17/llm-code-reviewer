# tests/test_reviewer.py — Unit Tests for reviewer.py
# Run with: pytest tests/ from the project root

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from reviewer import build_prompt, call_llm_api


class TestBuildPrompt:

    def test_prompt_contains_language(self):
        """TC-01 partial: Verify prompt includes the language."""
        prompt = build_prompt('print(x)', 'python')
        assert 'python' in prompt.lower()

    def test_prompt_contains_code(self):
        """TC-01 partial: Verify prompt includes the submitted code."""
        prompt = build_prompt('print(x)', 'python')
        assert 'print(x)' in prompt

    def test_prompt_contains_three_sections(self):
        """Verify prompt requests BUGS, SECURITY, QUALITY sections."""
        prompt = build_prompt('x = 1', 'python')
        assert 'BUGS:' in prompt
        assert 'SECURITY:' in prompt
        assert 'QUALITY:' in prompt


class TestCallLLMApi:

    @patch('reviewer.anthropic.Anthropic')
    def test_successful_api_call(self, mock_anthropic_class):
        """TC-01: Successful API call returns response text."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_client.messages.create.return_value.content = [
            MagicMock(text="BUGS: None identified.\nSECURITY: None identified.\nQUALITY: Add docstring.")
        ]
        result = call_llm_api("test prompt")
        assert "QUALITY" in result

    @patch('reviewer.anthropic.Anthropic')
    def test_api_timeout_raises_runtime_error(self, mock_anthropic_class):
        """TC-04: API timeout should raise RuntimeError."""
        import anthropic as anthro
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_client.messages.create.side_effect = anthro.APITimeoutError(
            request=MagicMock()
        )
        with pytest.raises(RuntimeError, match='timed out'):
            call_llm_api('test prompt')

    @patch('reviewer.anthropic.Anthropic')
    def test_auth_error_raises_runtime_error(self, mock_anthropic_class):
        """Invalid API key raises RuntimeError with clear message."""
        import anthropic as anthro
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_client.messages.create.side_effect = anthro.AuthenticationError(
            message="invalid key", response=MagicMock(), body={}
        )
        with pytest.raises(RuntimeError, match='Invalid API key'):
            call_llm_api('test prompt')