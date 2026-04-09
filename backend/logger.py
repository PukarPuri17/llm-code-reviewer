# logger.py — Session Logging Module
# Saves each code review session to a local JSON log file.
# This is used for testing and for demonstrating usage in your documentation.

import json
import os
from datetime import datetime, timezone


LOG_FILE = "logs/sessions.json"


def log_session(language: str, code_length: int, results: dict) -> None:
    """
    Appends a session record to the local log file.

    Each log entry records:
    - timestamp: when the review happened
    - language: the programming language submitted
    - code_length: number of characters in the submitted code
    - bug_count, security_count, quality_count: how many issues were found

    Args:
        language (str): Programming language of the submitted code.
        code_length (int): Number of characters in the submitted code.
        results (dict): The parsed results dict from parser.py.
    """
    os.makedirs("logs", exist_ok=True)

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                log_data = json.load(f)
            except json.JSONDecodeError:
                log_data = []
    else:
        log_data = []

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat() ,
        "language": language,
        "code_length": code_length,
        "bug_count": len(results.get("bugs", [])),
        "security_count": len(results.get("security", [])),
        "quality_count": len(results.get("quality", [])),
    }

    log_data.append(entry)

    with open(LOG_FILE, "w") as f:
        json.dump(log_data, f, indent=2)