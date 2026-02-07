import re
from typing import Optional, Tuple, Dict, Any

def to_float(s: str) -> Optional[float]:
    if s is None:
        return None
    s2 = str(s).strip().replace(",", ".")
    m = re.search(r"[-+]?\d+(\.\d+)?", s2)
    if not m:
        return None
    try:
        return float(m.group(0))
    except Exception:
        return None

def parse_reference_range(text: str) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    if not text:
        return None, None, None
    t = str(text).strip().replace(",", ".")

    m = re.search(r"(\d+(\.\d+)?)\s*[\-\–]\s*(\d+(\.\d+)?)", t)
    if m:
        return float(m.group(1)), float(m.group(3)), text

    m2 = re.search(r"(?:<|<=)\s*(\d+(\.\d+)?)", t)
    if m2:
        return None, float(m2.group(1)), text

    m3 = re.search(r"(?:>|>=)\s*(\d+(\.\d+)?)", t)
    if m3:
        return float(m3.group(1)), None, text

    return None, None, text

def out_of_range(value: Optional[float], low: Optional[float], high: Optional[float]) -> Optional[bool]:
    if value is None:
        return None
    if low is not None and value < low:
        return True
    if high is not None and value > high:
        return True
    if low is None and high is None:
        return None
    return False

def normalize_extraction(extraction_raw: Dict[str, Any], filename: str) -> Dict[str, Any]:
    results = []
    for r in extraction_raw.get("results", []):
        test_name = (r.get("test_name") or "").strip()
        value_raw = (r.get("value_raw") or "").strip()
        unit = r.get("unit") or None
        ref_range = r.get("reference_range") or None

        value_num = to_float(value_raw)
        ref_low, ref_high, ref_text = parse_reference_range(ref_range or "")
        flag = out_of_range(value_num, ref_low, ref_high)

        results.append(
            {
                "test_name": test_name,
                "value_raw": value_raw,
                "value_num": value_num,
                "unit": unit,
                "ref_low": ref_low,
                "ref_high": ref_high,
                "ref_text": ref_text,
                "is_out_of_range": flag,
            }
        )

    return {
        "report_date": extraction_raw.get("report_date"),
        "source_filename": filename,
        "results": results,
        "notes": extraction_raw.get("notes", []),
    }
