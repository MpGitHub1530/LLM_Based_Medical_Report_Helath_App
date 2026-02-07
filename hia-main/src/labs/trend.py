from typing import Dict, List, Optional

def compute_trends(current_extraction: Dict, previous_extraction: Optional[Dict]) -> List[Dict]:
    if not previous_extraction:
        return []

    prev_map = {}
    for r in previous_extraction.get("results", []):
        k = (r.get("test_name") or "").strip().lower()
        if k and r.get("value_num") is not None:
            prev_map[k] = r

    trends = []
    for r in current_extraction.get("results", []):
        k = (r.get("test_name") or "").strip().lower()
        cur_val = r.get("value_num")
        if not k or cur_val is None:
            continue

        prev = prev_map.get(k)
        if not prev:
            continue

        prev_val = prev.get("value_num")
        if prev_val is None:
            continue

        if cur_val > prev_val:
            direction = "up"
        elif cur_val < prev_val:
            direction = "down"
        else:
            direction = "stable"

        trends.append(
            {
                "test_name": r.get("test_name"),
                "current_value": cur_val,
                "previous_value": prev_val,
                "direction": direction,
                "unit": r.get("unit"),
            }
        )

    return trends
