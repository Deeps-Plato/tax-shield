"""Schedule D — Capital Gains and Losses field definitions."""

FORM_NAME = "Schedule D (Form 1040)"
FORM_YEAR = 2025

FIELDS = {
    "name": {"label": "Name(s) shown on return", "type": "text"},
    "ssn": {"label": "Your SSN", "type": "text"},
    # Part I — Short-Term (held one year or less)
    "st_proceeds": {"label": "1a - Short-term totals from 8949 Part I", "type": "currency"},
    "st_cost_basis": {"label": "1b - Cost or other basis", "type": "currency"},
    "st_adjustments": {"label": "1c - Adjustments", "type": "currency"},
    "st_gain_loss": {"label": "1d - Gain or (loss)", "type": "currency", "computed": True},
    "st_carryover": {
        "label": "6 - Short-term capital loss carryover",
        "type": "currency",
        "line": 6,
    },
    "net_st_gain_loss": {
        "label": "7 - Net short-term capital gain or (loss)",
        "type": "currency",
        "line": 7,
        "computed": True,
    },
    # Part II — Long-Term (held more than one year)
    "lt_proceeds": {"label": "8a - Long-term totals from 8949 Part II", "type": "currency"},
    "lt_cost_basis": {"label": "8b - Cost or other basis", "type": "currency"},
    "lt_adjustments": {"label": "8c - Adjustments", "type": "currency"},
    "lt_gain_loss": {"label": "8d - Gain or (loss)", "type": "currency", "computed": True},
    "lt_distributions": {
        "label": "11 - Capital gain distributions",
        "type": "currency",
        "line": 11,
    },
    "lt_carryover": {
        "label": "14 - Long-term capital loss carryover",
        "type": "currency",
        "line": 14,
    },
    "net_lt_gain_loss": {
        "label": "15 - Net long-term capital gain or (loss)",
        "type": "currency",
        "line": 15,
        "computed": True,
    },
    # Part III — Summary
    "net_st": {"label": "16 - Net short-term (from line 7)", "type": "currency", "line": 16},
    "net_lt": {"label": "17 - Net long-term (from line 15)", "type": "currency", "line": 17},
    "total_gain_loss": {
        "label": "21 - Total capital gain or (loss)",
        "type": "currency",
        "line": 21,
        "computed": True,
    },
}

# Long-term capital gains tax rates (2025)
LT_RATES = {
    "0%": {"single": 48_350, "mfj": 96_700},
    "15%": {"single": 533_400, "mfj": 600_050},
    "20%": {"single": float("inf"), "mfj": float("inf")},
}
