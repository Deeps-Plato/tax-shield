"""Form 1120-S — U.S. Income Tax Return for an S Corporation."""

FORM_NAME = "Form 1120-S"
FORM_YEAR = 2025

FIELDS = {
    "corp_name": {"label": "Name of corporation", "type": "text"},
    "ein": {"label": "Employer ID number", "type": "text"},
    "address": {"label": "Address", "type": "text"},
    "date_incorporated": {"label": "Date incorporated", "type": "date"},
    "business_activity_code": {"label": "Business activity code", "type": "text"},
    # Income
    "gross_receipts": {"label": "1a - Gross receipts or sales", "type": "currency", "line": "1a"},
    "returns_allowances": {
        "label": "1b - Returns and allowances",
        "type": "currency",
        "line": "1b",
    },
    "cogs": {"label": "2 - Cost of goods sold", "type": "currency", "line": 2},
    "gross_profit": {"label": "3 - Gross profit", "type": "currency", "line": 3, "computed": True},
    "net_gain_loss": {"label": "4 - Net gain (loss) from Form 4797", "type": "currency", "line": 4},
    "other_income": {"label": "5 - Other income (loss)", "type": "currency", "line": 5},
    "total_income": {
        "label": "6 - Total income (loss)",
        "type": "currency",
        "line": 6,
        "computed": True,
    },
    # Deductions
    "compensation_officers": {
        "label": "7 - Compensation of officers",
        "type": "currency",
        "line": 7,
    },
    "salaries_wages": {"label": "8 - Salaries and wages", "type": "currency", "line": 8},
    "repairs_maintenance": {"label": "9 - Repairs and maintenance", "type": "currency", "line": 9},
    "bad_debts": {"label": "10 - Bad debts", "type": "currency", "line": 10},
    "rents": {"label": "11 - Rents", "type": "currency", "line": 11},
    "taxes_licenses": {"label": "12 - Taxes and licenses", "type": "currency", "line": 12},
    "interest": {"label": "13 - Interest", "type": "currency", "line": 13},
    "depreciation": {"label": "14 - Depreciation", "type": "currency", "line": 14},
    "advertising": {"label": "16 - Advertising", "type": "currency", "line": 16},
    "pension_plans": {
        "label": "17 - Pension, profit-sharing plans",
        "type": "currency",
        "line": 17,
    },
    "employee_benefit": {"label": "18 - Employee benefit programs", "type": "currency", "line": 18},
    "other_deductions": {"label": "19 - Other deductions", "type": "currency", "line": 19},
    "total_deductions": {
        "label": "20 - Total deductions",
        "type": "currency",
        "line": 20,
        "computed": True,
    },
    "ordinary_business_income": {
        "label": "21 - Ordinary business income (loss)",
        "type": "currency",
        "line": 21,
        "computed": True,
    },
}
