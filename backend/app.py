# app.py — Flask Application Entry Point
# This file wires everything together.
# It defines the HTTP endpoints that the frontend calls.

from flask import Flask, request, jsonify
from flask_cors import CORS

from reviewer import build_prompt, call_llm_api
from parser import parse_response
from logger import log_session

app = Flask(__name__)
CORS(app)  # Allows the frontend HTML file to call this API

MAX_INPUT_LENGTH = 10_000  # Reject inputs over 10,000 characters


@app.route('/api/review', methods=['POST'])
def review_code():
    """
    Main endpoint: accepts source code and returns structured AI feedback.

    Request JSON:  { "code": "...", "language": "python" }
    Response JSON: { "bugs": [...], "security": [...], "quality": [...] }
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body must be JSON.'}), 400

    code = data.get('code', '').strip()
    language = data.get('language', '').strip()

    if not code:
        return jsonify({'error': 'Code cannot be empty.'}), 400

    if not language:
        return jsonify({'error': 'Language must be specified.'}), 400

    if len(code) > MAX_INPUT_LENGTH:
        return jsonify({'error': f'Input exceeds {MAX_INPUT_LENGTH:,} character limit.'}), 413

    try:
        prompt = build_prompt(code, language)
        raw_response = call_llm_api(prompt)
        structured = parse_response(raw_response)
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500

    log_session(language, len(code), structured)

    return jsonify(structured), 200


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check — visit http://localhost:5000/health to confirm server is running.
    """
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)