import re

def redact_identifiers(text: str) -> str:
    if not text:
        return text

    t = text

    # Email
    t = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "[REDACTED_EMAIL]", t)

    # Phone numbers simple patterns
    t = re.sub(r"\b(\+?\d{1,3}[\s-]?)?(\(?\d{2,4}\)?[\s-]?)?\d{3,4}[\s-]?\d{3,4}\b", "[REDACTED_PHONE]", t)

    # Dates of birth like patterns
    t = re.sub(r"\b(DOB|Date of Birth|Birth Date)\s*[: ]\s*\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}\b", "[REDACTED_DOB]", t, flags=re.IGNORECASE)

    # IDs and MRN like patterns
    t = re.sub(r"\b(MRN|Patient ID|Patient No|Account No|Report ID)\s*[: ]\s*[A-Za-z0-9\-]+\b", "[REDACTED_ID]", t, flags=re.IGNORECASE)

    # Names lines
    t = re.sub(r"\b(Name|Patient Name)\s*[: ]\s*[A-Za-z ,.'-]{2,}\b", "[REDACTED_NAME]", t, flags=re.IGNORECASE)

    # Addresses simple
    t = re.sub(r"\b(Address)\s*[: ]\s*.+", "Address: [REDACTED_ADDRESS]", t, flags=re.IGNORECASE)

    return t
