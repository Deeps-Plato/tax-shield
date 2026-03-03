"""Form W-2 — Wage and Tax Statement field definitions."""

FORM_NAME = "Form W-2"
FORM_YEAR = 2025

FIELDS = {
    # Employer info
    "employer_ein": {"label": "b - Employer's EIN", "type": "text"},
    "employer_name": {"label": "c - Employer's name", "type": "text"},
    "employer_address": {"label": "c - Employer's address", "type": "text"},
    # Employee info
    "employee_ssn": {"label": "a - Employee's SSN", "type": "text"},
    "employee_name": {"label": "e - Employee's name", "type": "text"},
    "employee_address": {"label": "f - Employee's address", "type": "text"},
    # Boxes
    "wages_tips": {"label": "1 - Wages, tips, other compensation", "type": "currency", "box": 1},
    "federal_withheld": {"label": "2 - Federal income tax withheld", "type": "currency", "box": 2},
    "ss_wages": {"label": "3 - Social security wages", "type": "currency", "box": 3},
    "ss_withheld": {"label": "4 - Social security tax withheld", "type": "currency", "box": 4},
    "medicare_wages": {"label": "5 - Medicare wages and tips", "type": "currency", "box": 5},
    "medicare_withheld": {"label": "6 - Medicare tax withheld", "type": "currency", "box": 6},
    "ss_tips": {"label": "7 - Social security tips", "type": "currency", "box": 7},
    "allocated_tips": {"label": "8 - Allocated tips", "type": "currency", "box": 8},
    "dependent_care": {"label": "10 - Dependent care benefits", "type": "currency", "box": 10},
    "nonqualified_plans": {"label": "11 - Nonqualified plans", "type": "currency", "box": 11},
    "box_12a_code": {"label": "12a - Code", "type": "text"},
    "box_12a_amount": {"label": "12a - Amount", "type": "currency"},
    "box_13_statutory": {"label": "13 - Statutory employee", "type": "boolean"},
    "box_13_retirement": {"label": "13 - Retirement plan", "type": "boolean"},
    "box_13_sick_pay": {"label": "13 - Third-party sick pay", "type": "boolean"},
    "state": {"label": "15 - State", "type": "text"},
    "state_id": {"label": "15 - State employer ID", "type": "text"},
    "state_wages": {"label": "16 - State wages", "type": "currency", "box": 16},
    "state_withheld": {"label": "17 - State income tax", "type": "currency", "box": 17},
    "local_wages": {"label": "18 - Local wages", "type": "currency", "box": 18},
    "local_withheld": {"label": "19 - Local income tax", "type": "currency", "box": 19},
    "locality_name": {"label": "20 - Locality name", "type": "text"},
}

# 2025 Social Security wage base
SS_WAGE_BASE = 176_100
SS_RATE = 0.062
MEDICARE_RATE = 0.0145
ADDITIONAL_MEDICARE_RATE = 0.009  # above $200K single / $250K MFJ
