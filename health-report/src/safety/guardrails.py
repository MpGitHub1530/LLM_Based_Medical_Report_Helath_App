import re

DISCLAIMER = (
    "Informational and educational only. Not diagnostic. Not medical advice. "
    "Not a substitute for a licensed clinician. Do not use for emergencies."
)

DIAGNOSIS = [
    r"\bdiagnos(e|is|ing)\b",
    r"\bwhat do i have\b",
    r"\bdo i have\b",
    r"\bdoes this mean i have\b",
]

TREATMENT = [
    r"\bwhat should i take\b",
    r"\bmedication\b",
    r"\bdose\b",
    r"\btreatment\b",
]

EMERGENCY = [
    r"\bemergency\b",
    r"\burgent\b",
    r"\bgo to (the )?er\b",
    r"\bcall an ambulance\b",
]

def check_request(text: str):
    t = (text or "").lower()

    for p in DIAGNOSIS:
        if re.search(p, t):
            return False, "I cannot help with diagnosis. Please consult a licensed clinician."

    for p in TREATMENT:
        if re.search(p, t):
            return False, "I cannot help with treatment or medication advice. Please consult a licensed clinician."

    for p in EMERGENCY:
        if re.search(p, t):
            return False, "I cannot help with emergency guidance. Please contact local emergency services or a clinician."

    return True, ""
