"""Form 1065 — U.S. Return of Partnership Income."""

FORM_NAME = "Form 1065"
FORM_YEAR = 2025

FIELDS = {
    "partnership_name": {"label": "Name of partnership", "type": "text"},
    "ein": {"label": "Employer ID number", "type": "text"},
    "address": {"label": "Address", "type": "text"},
    "business_code": {"label": "Principal business activity code", "type": "text"},
    "date_started": {"label": "Date business started", "type": "date"},
    # Income
    "gross_receipts": {"label": "1a - Gross receipts or sales", "type": "currency", "line": "1a"},
    "returns_allowances": {
        "label": "1b - Returns and allowances",
        "type": "currency",
        "line": "1b",
    },
    "cogs": {"label": "2 - Cost of goods sold", "type": "currency", "line": 2},
    "gross_profit": {"label": "3 - Gross profit", "type": "currency", "line": 3, "computed": True},
    "ordinary_income_other": {"label": "4-7 - Other income items", "type": "currency"},
    "total_income": {
        "label": "8 - Total income (loss)",
        "type": "currency",
        "line": 8,
        "computed": True,
    },
    # Deductions
    "salaries_wages": {"label": "9 - Salaries and wages", "type": "currency", "line": 9},
    "guaranteed_payments": {
        "label": "10 - Guaranteed payments to partners",
        "type": "currency",
        "line": 10,
    },
    "repairs": {"label": "11 - Repairs and maintenance", "type": "currency", "line": 11},
    "bad_debts": {"label": "12 - Bad debts", "type": "currency", "line": 12},
    "rent": {"label": "13 - Rent", "type": "currency", "line": 13},
    "taxes_licenses": {"label": "14 - Taxes and licenses", "type": "currency", "line": 14},
    "interest": {"label": "15 - Interest", "type": "currency", "line": 15},
    "depreciation": {"label": "16a - Depreciation", "type": "currency", "line": "16a"},
    "retirement_plans": {"label": "18 - Retirement plans, etc.", "type": "currency", "line": 18},
    "employee_benefit": {"label": "19 - Employee benefit programs", "type": "currency", "line": 19},
    "other_deductions": {"label": "20 - Other deductions", "type": "currency", "line": 20},
    "total_deductions": {
        "label": "21 - Total deductions",
        "type": "currency",
        "line": 21,
        "computed": True,
    },
    "ordinary_business_income": {
        "label": "22 - Ordinary business income (loss)",
        "type": "currency",
        "line": 22,
        "computed": True,
    },
}
