"""Schedule C — Profit or Loss From Business field definitions."""

FORM_NAME = "Schedule C (Form 1040)"
FORM_YEAR = 2025

FIELDS = {
    "name": {"label": "Name of proprietor", "type": "text"},
    "ssn": {"label": "SSN", "type": "text"},
    "business_name": {"label": "A - Principal business or profession", "type": "text"},
    "business_code": {"label": "B - Business code", "type": "text"},
    "ein": {"label": "D - EIN", "type": "text"},
    "business_address": {"label": "E - Business address", "type": "text"},
    "accounting_method": {
        "label": "F - Accounting method",
        "type": "select",
        "options": ["Cash", "Accrual", "Other"],
    },
    "materially_participated": {"label": "G - Did you materially participate?", "type": "boolean"},
    # Income
    "gross_receipts": {"label": "1 - Gross receipts or sales", "type": "currency", "line": 1},
    "returns_allowances": {"label": "2 - Returns and allowances", "type": "currency", "line": 2},
    "cogs": {"label": "4 - Cost of goods sold", "type": "currency", "line": 4},
    "gross_income": {"label": "5 - Gross income", "type": "currency", "line": 5, "computed": True},
    "other_income": {"label": "6 - Other income", "type": "currency", "line": 6},
    "gross_income_total": {
        "label": "7 - Gross income total",
        "type": "currency",
        "line": 7,
        "computed": True,
    },
    # Expenses
    "advertising": {"label": "8 - Advertising", "type": "currency", "line": 8},
    "car_truck": {"label": "9 - Car and truck expenses", "type": "currency", "line": 9},
    "commissions": {"label": "10 - Commissions and fees", "type": "currency", "line": 10},
    "contract_labor": {"label": "11 - Contract labor", "type": "currency", "line": 11},
    "depletion": {"label": "12 - Depletion", "type": "currency", "line": 12},
    "depreciation": {"label": "13 - Depreciation and Section 179", "type": "currency", "line": 13},
    "employee_benefit": {"label": "14 - Employee benefit programs", "type": "currency", "line": 14},
    "insurance": {"label": "15 - Insurance (other than health)", "type": "currency", "line": 15},
    "interest_mortgage": {"label": "16a - Mortgage interest", "type": "currency", "line": "16a"},
    "interest_other": {"label": "16b - Other interest", "type": "currency", "line": "16b"},
    "legal_professional": {
        "label": "17 - Legal and professional services",
        "type": "currency",
        "line": 17,
    },
    "office_expense": {"label": "18 - Office expense", "type": "currency", "line": 18},
    "pension_profit_sharing": {
        "label": "19 - Pension and profit-sharing plans",
        "type": "currency",
        "line": 19,
    },
    "rent_vehicles": {
        "label": "20a - Rent — vehicles, machinery, equipment",
        "type": "currency",
        "line": "20a",
    },
    "rent_property": {
        "label": "20b - Rent — other business property",
        "type": "currency",
        "line": "20b",
    },
    "repairs": {"label": "21 - Repairs and maintenance", "type": "currency", "line": 21},
    "supplies": {"label": "22 - Supplies", "type": "currency", "line": 22},
    "taxes_licenses": {"label": "23 - Taxes and licenses", "type": "currency", "line": 23},
    "travel": {"label": "24a - Travel", "type": "currency", "line": "24a"},
    "meals": {"label": "24b - Deductible meals", "type": "currency", "line": "24b"},
    "utilities": {"label": "25 - Utilities", "type": "currency", "line": 25},
    "wages": {"label": "26 - Wages", "type": "currency", "line": 26},
    "other_expenses": {"label": "27a - Other expenses", "type": "currency", "line": "27a"},
    "total_expenses": {
        "label": "28 - Total expenses",
        "type": "currency",
        "line": 28,
        "computed": True,
    },
    # Net
    "net_profit_loss": {
        "label": "31 - Net profit or (loss)",
        "type": "currency",
        "line": 31,
        "computed": True,
    },
}
