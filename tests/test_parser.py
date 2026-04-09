# tests/test_parser.py — Unit Tests for parser.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from parser import parse_response


class TestParseResponse:

    def test_well_formed_response(self):
        """TC-05: Parse a well-formed LLM response into 3 categories."""
        raw = "BUGS: - Missing null check\nSECURITY: None identified.\nQUALITY: - Add docstring"
        result = parse_response(raw)
        assert len(result['bugs']) == 1
        assert result['security'] == []
        assert len(result['quality']) == 1

    def test_none_identified_returns_empty(self):
        """TC-06: 'None identified.' sections return empty lists."""
        raw = "BUGS: None identified.\nSECURITY: None identified.\nQUALITY: None identified."
        result = parse_response(raw)
        assert result == {'bugs': [], 'security': [], 'quality': []}

    def test_missing_sections_return_empty(self):
        """TC-06: Missing sections default to empty lists, no crash."""
        raw = "BUGS: - Off by one error"
        result = parse_response(raw)
        assert isinstance(result['security'], list)
        assert isinstance(result['quality'], list)

    def test_garbled_response_no_crash(self):
        """TC-07: Garbled LLM output returns empty dict, no exception."""
        raw = "Sorry, I cannot analyze this code at this time."
        result = parse_response(raw)
        assert result == {'bugs': [], 'security': [], 'quality': []}

    def test_multiple_items_per_section(self):
        """Multiple bullet points are parsed as separate items."""
        raw = "BUGS:\n- Issue one\n- Issue two\n- Issue three\nSECURITY: None identified.\nQUALITY: None identified."
        result = parse_response(raw)
        assert len(result['bugs']) == 3

    def test_strips_bullet_characters(self):
        """Bullet characters (-, *, •) are stripped from items."""
        raw = "BUGS:\n• Bullet point\n* Asterisk point\nSECURITY: None identified.\nQUALITY: None identified."
        result = parse_response(raw)
        for item in result['bugs']:
            assert not item.startswith(('•', '*', '-'))