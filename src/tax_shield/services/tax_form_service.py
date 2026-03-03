"""Tax form data computation and PDF generation."""

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tax_shield.models.db_models import TaxRecord, Transaction, User, UserItem


async def compute_form_data(
    db: AsyncSession, user: User, form_type: str, tax_year: int
) -> dict:
    """Compute form field data from user's items and transactions."""
    # Get user's saved items for this year
    items_result = await db.execute(
        select(UserItem).where(
            UserItem.user_id == user.id,
            UserItem.tax_year == tax_year,
        )
    )
    user_items = items_result.scalars().all()

    # Get categorized transactions
    txns_result = await db.execute(
        select(Transaction).where(
            Transaction.user_id == user.id,
            Transaction.tax_year == tax_year,
            Transaction.is_deductible.is_(True),
        )
    )
    deductible_txns = txns_result.scalars().all()

    total_deductions = sum(ui.estimated_savings or 0 for ui in user_items)
    total_expenses = sum(t.amount for t in deductible_txns)

    # Build form-specific data
    if form_type == "schedule_c":
        return _schedule_c_data(user, user_items, deductible_txns, total_expenses)
    elif form_type == "schedule_a":
        return _schedule_a_data(user, user_items, deductible_txns, total_deductions)
    elif form_type == "1040":
        return _form_1040_data(user, user_items, total_deductions)
    else:
        return {
            "form_type": form_type,
            "tax_year": tax_year,
            "user_name": user.name,
            "total_deductions": total_deductions,
            "total_expenses": total_expenses,
            "items_count": len(user_items),
            "transactions_count": len(deductible_txns),
            "status": "draft",
            "note": "Detailed computation not yet implemented for this form type",
        }


def _schedule_c_data(
    user: User, items: list, transactions: list, total_expenses: float
) -> dict:
    # Group expenses by category
    expense_categories: dict[str, float] = {}
    for txn in transactions:
        cat = str(txn.tax_category_id or "uncategorized")
        expense_categories[cat] = expense_categories.get(cat, 0) + txn.amount

    return {
        "form_type": "Schedule C",
        "name": user.name,
        "gross_receipts": 0,  # User needs to fill
        "total_expenses": total_expenses,
        "expense_breakdown": expense_categories,
        "net_profit_loss": -total_expenses,  # Placeholder until income entered
        "items_claimed": len(items),
        "status": "draft",
    }


def _schedule_a_data(
    user: User, items: list, transactions: list, total_deductions: float
) -> dict:
    return {
        "form_type": "Schedule A",
        "name": user.name,
        "medical_dental": 0,
        "taxes_paid": 0,
        "interest_paid": 0,
        "charitable": 0,
        "other_deductions": total_deductions,
        "total_itemized": total_deductions,
        "items_claimed": len(items),
        "status": "draft",
    }


def _form_1040_data(user: User, items: list, total_deductions: float) -> dict:
    return {
        "form_type": "1040",
        "name": user.name,
        "filing_status": user.filing_type or "single",
        "total_income": 0,  # User needs to fill
        "adjustments": 0,
        "agi": 0,
        "deductions": total_deductions,
        "taxable_income": 0,
        "tax_owed": 0,
        "credits": 0,
        "total_payments": 0,
        "refund_or_owed": 0,
        "status": "draft",
    }


def generate_pdf(record: TaxRecord) -> bytes:
    """Generate a PDF for a tax record."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, topMargin=0.75 * inch)
    styles = getSampleStyleSheet()
    elements: list = []

    # Title
    title_style = ParagraphStyle(
        "FormTitle", parent=styles["Title"], fontSize=16, spaceAfter=12
    )
    elements.append(
        Paragraph(f"Tax Form: {record.form_type} — Tax Year {record.tax_year}", title_style)
    )
    elements.append(Spacer(1, 12))

    # Status
    status_style = ParagraphStyle(
        "Status", parent=styles["Normal"], fontSize=12, textColor=colors.red
    )
    elements.append(Paragraph(f"Status: {record.status.upper()} — FOR REVIEW ONLY", status_style))
    elements.append(Spacer(1, 24))

    # Data table
    data = record.data or {}
    table_data = [["Field", "Value"]]
    for key, value in data.items():
        if isinstance(value, dict):
            value = ", ".join(f"{k}: ${v:,.2f}" if isinstance(v, (int, float)) else f"{k}: {v}" for k, v in value.items())
        elif isinstance(value, (int, float)) and key not in ("tax_year", "items_claimed", "transactions_count"):
            value = f"${value:,.2f}"
        table_data.append([key.replace("_", " ").title(), str(value)])

    if len(table_data) > 1:
        table = Table(table_data, colWidths=[3 * inch, 4 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e40af")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4ff")]),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        elements.append(table)

    elements.append(Spacer(1, 24))
    disclaimer = ParagraphStyle("Disclaimer", parent=styles["Normal"], fontSize=8, textColor=colors.grey)
    elements.append(
        Paragraph(
            "This document is a DRAFT generated by Tax Shield for review purposes only. "
            "It is not a substitute for professional tax advice. Consult your tax professional "
            "before filing. Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M"),
            disclaimer,
        )
    )

    doc.build(elements)
    return buf.getvalue()
