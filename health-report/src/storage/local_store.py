import os
import json
from datetime import datetime
from typing import Optional, Dict, List

DATA_DIR = os.path.join("data", "reports")

def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def save_report(user_id: str, filename: str, extraction: Dict, explanation: Dict) -> str:
    _ensure_dir(DATA_DIR)
    user_dir = os.path.join(DATA_DIR, user_id)
    _ensure_dir(user_dir)

    report_id = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    path = os.path.join(user_dir, f"{report_id}.json")

    bundle = {
        "report_id": report_id,
        "created_at": datetime.utcnow().isoformat(),
        "filename": filename,
        "extraction": extraction,
        "explanation": explanation,
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(bundle, f, ensure_ascii=False, indent=2)

    return report_id

def list_reports(user_id: str) -> List[Dict]:
    user_dir = os.path.join(DATA_DIR, user_id)
    if not os.path.isdir(user_dir):
        return []

    items = []
    for name in sorted(os.listdir(user_dir), reverse=True):
        if name.endswith(".json"):
            items.append({"report_id": name.replace(".json", ""), "path": os.path.join(user_dir, name)})
    return items

def load_report(user_id: str, report_id: str) -> Optional[Dict]:
    user_dir = os.path.join(DATA_DIR, user_id)
    path = os.path.join(user_dir, f"{report_id}.json")
    if not os.path.isfile(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_most_recent_report(user_id: str) -> Optional[Dict]:
    reports = list_reports(user_id)
    if not reports:
        return None
    rid = reports[0]["report_id"]
    return load_report(user_id, rid)
