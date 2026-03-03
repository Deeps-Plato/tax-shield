"""CSV import service — the actual import logic is in routes/transactions.py upload_csv.

This module provides utilities for detecting CSV formats and column mapping."""

# Common column name mappings for various bank CSV exports
COLUMN_MAPS = {
    "chase": {
        "Transaction Date": "date",
        "Post Date": "date",
        "Description": "description",
        "Amount": "amount",
        "Category": "plaid_category",
    },
    "amex": {
        "Date": "date",
        "Description": "description",
        "Amount": "amount",
        "Category": "plaid_category",
    },
    "bofa": {
        "Date": "date",
        "Description": "description",
        "Amount": "amount",
    },
    "citi": {
        "Date": "date",
        "Description": "description",
        "Debit": "amount",
        "Credit": "credit",
    },
    "generic": {
        "date": "date",
        "description": "description",
        "amount": "amount",
        "merchant": "merchant",
        "category": "plaid_category",
    },
}


def detect_csv_format(headers: list[str]) -> str:
    """Detect which bank format a CSV is from based on headers."""
    header_set = {h.lower().strip() for h in headers}

    if "post date" in header_set:
        return "chase"
    if {"date", "description", "amount", "category"} <= header_set:
        return "amex"
    if "debit" in header_set and "credit" in header_set:
        return "citi"
    return "generic"
