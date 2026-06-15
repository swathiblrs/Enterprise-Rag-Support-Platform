import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "query_logs.jsonl"


def log_query(entry: Dict[str, Any]) -> None:
    LOG_DIR.mkdir(exist_ok=True)

    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        **entry,
    }

    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(log_entry) + "\n")


def read_logs() -> list:
    if not LOG_FILE.exists():
        return []

    logs = []
    with LOG_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                logs.append(json.loads(line))

    return logs