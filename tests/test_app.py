# tests/test_app.py — Integration Tests for Flask API
# Tests the full request-response cycle WITHOUT calling the real LLM API.
# We mock the LLM call so tests run fast and don't cost money.

import sys
import os
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app


@pytest.fixture
def client():
    """Creates a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


MOCK_LLM_RESPONSE = "BUGS: None identified.\nSECURITY: None identified.\nQUALITY: - Add type hints."


@patch('app.call_llm_api', return_value=MOCK_LLM_RESPONSE)
def test_valid_review_request(mock_llm, client):
    """TC-08: Valid payload returns 200 with structured JSON."""
    response = client.post('/api/review',
                           json={'code': 'def add(a, b): return a + b', 'language': 'python'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'bugs' in data and 'security' in data and 'quality' in data


def test_missing_language_returns_400(client):
    """TC-09: Missing language field returns 400 Bad Request."""
    response = client.post('/api/review', json={'code': 'x = 1'})
    assert response.status_code == 400


def test_empty_code_returns_400(client):
    """TC-02: Empty code string returns 400 validation error."""
    response = client.post('/api/review', json={'code': '', 'language': 'python'})
    assert response.status_code == 400


def test_oversized_input_returns_413(client):
    """TC-03: Input over 10,000 chars returns 413 error."""
    response = client.post('/api/review',
                           json={'code': 'x' * 15000, 'language': 'python'})
    assert response.status_code == 413


def test_health_check(client):
    """Health endpoint returns 200 and status ok."""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'ok'


def test_missing_code_field_returns_400(client):
    """Missing code field entirely returns 400."""
    response = client.post('/api/review', json={'language': 'python'})
    assert response.status_code == 400


@patch('app.call_llm_api', side_effect=RuntimeError("API timed out"))
def test_llm_error_returns_500(mock_llm, client):
    """TC-04: LLM failure returns 500 with error message."""
    response = client.post('/api/review',
                           json={'code': 'print("hello")', 'language': 'python'})
    assert response.status_code == 500
    assert 'error' in response.get_json()