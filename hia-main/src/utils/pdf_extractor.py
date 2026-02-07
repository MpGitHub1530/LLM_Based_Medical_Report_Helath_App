import pdfplumber
from config.app_config import MAX_PDF_PAGES
from utils.validators import validate_pdf_file, validate_pdf_content
from utils.redaction import redact_identifiers


def extract_text_from_pdf(pdf_file):
    """Extract and validate text from PDF file."""
    try:
        is_valid, error = validate_pdf_file(pdf_file)
        if not is_valid:
            return error

        text = ""

        with pdfplumber.open(pdf_file) as pdf:
            if len(pdf.pages) > MAX_PDF_PAGES:
                return f"PDF exceeds maximum page limit of {MAX_PDF_PAGES}"

            for page in pdf.pages:
                extracted = page.extract_text() or ""

                # If normal text extraction fails, try extracting tables
                if not extracted.strip():
                    tables = page.extract_tables() or []
                    table_text_lines = []
                    for tbl in tables:
                        for row in tbl:
                            if row:
                                row_clean = [
                                    str(cell).strip()
                                    for cell in row
                                    if cell is not None and str(cell).strip()
                                ]
                                if row_clean:
                                    table_text_lines.append("  ".join(row_clean))
                    extracted = "\n".join(table_text_lines)

                # If still empty, skip the page
                if extracted.strip():
                    text += extracted + "\n"

        if not text.strip():
            return "Could not extract text from PDF. The PDF may be scanned or image based. Please use a text based PDF."

        is_valid, error = validate_pdf_content(text)
        if not is_valid:
            return error

        return text

    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"


def extract_text_from_pdf_safe(pdf_file):
    """Return both raw and redacted text for privacy safe LLM use."""
    raw_text = extract_text_from_pdf(pdf_file)

    if not isinstance(raw_text, str):
        return {"error": "Could not extract text from PDF"}

    low = raw_text.lower()
    if "could not extract text" in low or low.startswith("error"):
        return {"error": raw_text}

    safe_text = redact_identifiers(raw_text)
    return {"raw_text": raw_text, "safe_text": safe_text}
