"""Form 1099 — Various Income Reporting field definitions."""

FORM_NAME = "Form 1099"
FORM_YEAR = 2025

# 1099-NEC (Nonemployee Compensation) — most common for contractors
FIELDS_1099_NEC = {
    "payer_name": {"label": "Payer's name", "type": "text"},
    "payer_tin": {"label": "Payer's TIN", "type": "text"},
    "payer_address": {"label": "Payer's address", "type": "text"},
    "recipient_name": {"label": "Recipient's name", "type": "text"},
    "recipient_tin": {"label": "Recipient's TIN", "type": "text"},
    "recipient_address": {"label": "Recipient's address", "type": "text"},
    "nonemployee_compensation": {
        "label": "1 - Nonemployee compensation",
        "type": "currency",
        "box": 1,
    },
    "federal_withheld": {"label": "4 - Federal income tax withheld", "type": "currency", "box": 4},
    "state_withheld": {"label": "5 - State tax withheld", "type": "currency", "box": 5},
    "state": {"label": "6 - State", "type": "text"},
    "state_id": {"label": "7 - State payer's ID", "type": "text"},
    "state_income": {"label": "State income", "type": "currency"},
}

# 1099-MISC — Miscellaneous income
FIELDS_1099_MISC = {
    "rents": {"label": "1 - Rents", "type": "currency", "box": 1},
    "royalties": {"label": "2 - Royalties", "type": "currency", "box": 2},
    "other_income": {"label": "3 - Other income", "type": "currency", "box": 3},
    "fishing_boat_proceeds": {"label": "5 - Fishing boat proceeds", "type": "currency", "box": 5},
    "medical_payments": {
        "label": "6 - Medical and health care payments",
        "type": "currency",
        "box": 6,
    },
    "crop_insurance": {"label": "9 - Crop insurance proceeds", "type": "currency", "box": 9},
    "gross_proceeds_attorney": {
        "label": "10 - Gross proceeds paid to an attorney",
        "type": "currency",
        "box": 10,
    },
    "section_409a_deferrals": {
        "label": "12 - Section 409A deferrals",
        "type": "currency",
        "box": 12,
    },
    "excess_golden_parachute": {
        "label": "13 - Excess golden parachute payments",
        "type": "currency",
        "box": 13,
    },
    "nonqualified_deferred": {
        "label": "14 - Nonqualified deferred compensation",
        "type": "currency",
        "box": 14,
    },
}

# Threshold for 1099-NEC filing
NEC_THRESHOLD = 600
