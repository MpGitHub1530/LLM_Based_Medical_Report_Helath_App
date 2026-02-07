import json
from safety.guardrails import check_request, DISCLAIMER
from storage.local_store import save_report, load_most_recent_report
from labs.trend import compute_trends
from labs.normalize import normalize_extraction
from services.ai_service import call_groq_json

EXTRACTION_SYSTEM = "Extract lab test rows from report text. Return only JSON. No diagnosis."

EXTRACTION_USER = """
Extract lab results into JSON.

Report text
{report_text}

Return JSON schema
{{
  "report_date": "optional string",
  "results": [
    {{
      "test_name": "string",
      "value_raw": "string",
      "unit": "optional string",
      "reference_range": "optional string"
    }}
  ],
  "notes": ["optional strings"]
}}

Rules
Only include tests clearly present
Use only the report reference ranges
If uncertain leave fields empty
Return JSON only
"""

EXPLANATION_SYSTEM = "Educational explanations only. No diagnosis. No treatment. No emergency guidance. Ground in extracted values only."

EXPLANATION_USER = """
Using this extracted JSON, create educational explanations grounded in the values and ranges.

User Question: "{user_question}"
If the user asked a question, answer it safely in the 'user_question_answer' field. If no question, leave it empty.

Extracted JSON
{extraction_json}

Return JSON schema
{{
  "disclaimer": "{disclaimer}",
  "user_question_answer": "optional answer to the user question",
  "items": [
    {{
      "test_name": "string",
      "summary": "short educational summary tied to the value and range when present",
      "what_it_measures": "plain language description",
      "how_to_discuss_with_doctor": ["questions the user can ask their doctor"],
      "grounded_in_report": "reference the value unit and range from the extraction"
    }}
  ],
  "general_questions_for_doctor": ["neutral questions"],
  "grounding_warnings": ["any uncertain places"]
}}

Return JSON only
"""

def process_lab_report(user_id: str, filename: str, report_text: str, user_question: str = ""):
    ok, msg = check_request(user_question)
    if not ok:
        return {"success": False, "error": msg}

    extraction_raw = call_groq_json(
        system=EXTRACTION_SYSTEM,
        user=EXTRACTION_USER.format(report_text=report_text),
    )

    extraction = normalize_extraction(extraction_raw, filename)

    prev = load_most_recent_report(user_id)
    prev_extraction = prev["extraction"] if prev else None
    trends = compute_trends(extraction, prev_extraction)

    explanation = call_groq_json(
        system=EXPLANATION_SYSTEM,
        user=EXPLANATION_USER.format(
            extraction_json=json.dumps(extraction, ensure_ascii=False),
            disclaimer=DISCLAIMER,
            user_question=user_question or "None",
        ),
    )

    save_report(user_id=user_id, filename=filename, extraction=extraction, explanation=explanation)

    return {"success": True, "extraction": extraction, "explanation": explanation, "trends": trends}
