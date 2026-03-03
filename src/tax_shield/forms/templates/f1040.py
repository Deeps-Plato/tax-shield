"""Form 1040 — Individual Income Tax Return field definitions."""

FORM_NAME = "Form 1040"
FORM_YEAR = 2025

FIELDS = {
    "filing_status": {
        "label": "Filing Status",
        "type": "select",
        "options": [
            "Single",
            "Married Filing Jointly",
            "Married Filing Separately",
            "Head of Household",
            "Qualifying Surviving Spouse",
        ],
    },
    "first_name": {"label": "First Name", "type": "text"},
    "last_name": {"label": "Last Name", "type": "text"},
    "ssn": {"label": "SSN", "type": "text"},
    # Income
    "wages": {"label": "1 - Wages, salaries, tips (W-2)", "type": "currency", "line": 1},
    "tax_exempt_interest": {"label": "2a - Tax-exempt interest", "type": "currency", "line": "2a"},
    "taxable_interest": {"label": "2b - Taxable interest", "type": "currency", "line": "2b"},
    "qualified_dividends": {"label": "3a - Qualified dividends", "type": "currency", "line": "3a"},
    "ordinary_dividends": {"label": "3b - Ordinary dividends", "type": "currency", "line": "3b"},
    "ira_distributions": {"label": "4a - IRA distributions", "type": "currency", "line": "4a"},
    "ira_taxable": {"label": "4b - Taxable amount", "type": "currency", "line": "4b"},
    "pensions": {"label": "5a - Pensions and annuities", "type": "currency", "line": "5a"},
    "pensions_taxable": {"label": "5b - Taxable amount", "type": "currency", "line": "5b"},
    "social_security": {"label": "6a - Social security benefits", "type": "currency", "line": "6a"},
    "social_security_taxable": {"label": "6b - Taxable amount", "type": "currency", "line": "6b"},
    "capital_gain_loss": {
        "label": "7 - Capital gain or loss (Schedule D)",
        "type": "currency",
        "line": 7,
    },
    "other_income": {"label": "8 - Other income (Schedule 1)", "type": "currency", "line": 8},
    "total_income": {"label": "9 - Total income", "type": "currency", "line": 9, "computed": True},
    # Adjustments
    "adjustments": {
        "label": "10 - Adjustments to income (Schedule 1)",
        "type": "currency",
        "line": 10,
    },
    "agi": {
        "label": "11 - Adjusted gross income",
        "type": "currency",
        "line": 11,
        "computed": True,
    },
    # Deductions
    "standard_deduction": {
        "label": "12 - Standard deduction or itemized (Sch A)",
        "type": "currency",
        "line": 12,
    },
    "qbi_deduction": {
        "label": "13 - Qualified business income deduction",
        "type": "currency",
        "line": 13,
    },
    "total_deductions": {
        "label": "14 - Total deductions",
        "type": "currency",
        "line": 14,
        "computed": True,
    },
    "taxable_income": {
        "label": "15 - Taxable income",
        "type": "currency",
        "line": 15,
        "computed": True,
    },
    # Tax and Credits
    "tax": {"label": "16 - Tax", "type": "currency", "line": 16},
    "child_tax_credit": {"label": "19 - Child tax credit", "type": "currency", "line": 19},
    "other_credits": {"label": "21 - Other credits", "type": "currency", "line": 21},
    "total_tax": {"label": "24 - Total tax", "type": "currency", "line": 24, "computed": True},
    # Payments
    "federal_withheld": {
        "label": "25 - Federal income tax withheld",
        "type": "currency",
        "line": 25,
    },
    "estimated_payments": {"label": "26 - Estimated tax payments", "type": "currency", "line": 26},
    "total_payments": {
        "label": "33 - Total payments",
        "type": "currency",
        "line": 33,
        "computed": True,
    },
    # Refund / Owed
    "overpaid": {"label": "34 - Overpaid", "type": "currency", "line": 34, "computed": True},
    "amount_owed": {
        "label": "37 - Amount you owe",
        "type": "currency",
        "line": 37,
        "computed": True,
    },
}

STANDARD_DEDUCTIONS_2025 = {
    "Single": 15_000,
    "Married Filing Jointly": 30_000,
    "Married Filing Separately": 15_000,
    "Head of Household": 22_500,
    "Qualifying Surviving Spouse": 30_000,
}
