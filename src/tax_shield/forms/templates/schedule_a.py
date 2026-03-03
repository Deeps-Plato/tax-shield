"""Schedule A — Itemized Deductions field definitions."""

FORM_NAME = "Schedule A (Form 1040)"
FORM_YEAR = 2025

FIELDS = {
    "name": {"label": "Name(s) shown on Form 1040", "type": "text"},
    "ssn": {"label": "Your SSN", "type": "text"},
    # Medical and Dental
    "medical_dental_expenses": {
        "label": "1 - Medical and dental expenses",
        "type": "currency",
        "line": 1,
    },
    "agi_amount": {
        "label": "2 - Enter amount from Form 1040, line 11 (AGI)",
        "type": "currency",
        "line": 2,
    },
    "agi_7_5_percent": {
        "label": "3 - Multiply line 2 by 7.5%",
        "type": "currency",
        "line": 3,
        "computed": True,
    },
    "medical_deduction": {
        "label": "4 - Subtract line 3 from line 1",
        "type": "currency",
        "line": 4,
        "computed": True,
    },
    # Taxes You Paid
    "state_local_income_tax": {
        "label": "5a - State and local income taxes",
        "type": "currency",
        "line": "5a",
    },
    "state_local_sales_tax": {
        "label": "5b - State and local sales taxes",
        "type": "currency",
        "line": "5b",
    },
    "real_estate_taxes": {"label": "5c - Real estate taxes", "type": "currency", "line": "5c"},
    "personal_property_taxes": {
        "label": "5d - Personal property taxes",
        "type": "currency",
        "line": "5d",
    },
    "salt_total": {
        "label": "5e - Total (limited to $10,000)",
        "type": "currency",
        "line": "5e",
        "computed": True,
    },
    "other_taxes": {"label": "6 - Other taxes", "type": "currency", "line": 6},
    "taxes_total": {
        "label": "7 - Total taxes paid",
        "type": "currency",
        "line": 7,
        "computed": True,
    },
    # Interest You Paid
    "mortgage_interest_1098": {
        "label": "8a - Home mortgage interest (Form 1098)",
        "type": "currency",
        "line": "8a",
    },
    "mortgage_interest_other": {
        "label": "8b - Home mortgage interest not reported on 1098",
        "type": "currency",
        "line": "8b",
    },
    "points": {"label": "8c - Points not reported on Form 1098", "type": "currency", "line": "8c"},
    "investment_interest": {"label": "9 - Investment interest", "type": "currency", "line": 9},
    "interest_total": {
        "label": "10 - Total interest paid",
        "type": "currency",
        "line": 10,
        "computed": True,
    },
    # Gifts to Charity
    "charity_cash": {"label": "11 - Gifts by cash or check", "type": "currency", "line": 11},
    "charity_non_cash": {
        "label": "12 - Other than by cash or check",
        "type": "currency",
        "line": 12,
    },
    "charity_carryover": {
        "label": "13 - Carryover from prior year",
        "type": "currency",
        "line": 13,
    },
    "charity_total": {
        "label": "14 - Total charitable gifts",
        "type": "currency",
        "line": 14,
        "computed": True,
    },
    # Other Deductions
    "casualty_losses": {"label": "15 - Casualty and theft losses", "type": "currency", "line": 15},
    "other_deductions": {"label": "16 - Other itemized deductions", "type": "currency", "line": 16},
    # Total
    "total_itemized": {
        "label": "17 - Total itemized deductions",
        "type": "currency",
        "line": 17,
        "computed": True,
    },
}

SALT_CAP = 10_000
