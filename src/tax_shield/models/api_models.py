from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

# ── Auth ──


class UserRegister(BaseModel):
    email: str
    password: str
    name: str


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: UUID
    email: str
    name: str
    role: str
    filing_type: str | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


# ── Categories ──


class CategoryOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    parent_id: int | None = None
    icon: str | None = None
    sort_order: int

    model_config = {"from_attributes": True}


class CategoryCreate(BaseModel):
    name: str
    description: str | None = None
    parent_id: int | None = None
    icon: str | None = None
    sort_order: int = 0


# ── Items ──


class ItemOut(BaseModel):
    id: int
    name: str
    description: str
    category_id: int
    deduction_type: str
    filing_types: list[str]
    irs_reference: str | None = None
    deduction_percentage: float | None = None
    max_amount: float | None = None
    conditions: str | None = None
    tax_year: int
    is_active: bool

    model_config = {"from_attributes": True}


class ItemCreate(BaseModel):
    name: str
    description: str
    category_id: int
    deduction_type: str = "deduction"
    filing_types: list[str] = []
    irs_reference: str | None = None
    deduction_percentage: float | None = None
    max_amount: float | None = None
    conditions: str | None = None
    tax_year: int = 2025


class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category_id: int | None = None
    deduction_type: str | None = None
    filing_types: list[str] | None = None
    irs_reference: str | None = None
    deduction_percentage: float | None = None
    max_amount: float | None = None
    conditions: str | None = None
    tax_year: int | None = None
    is_active: bool | None = None


# ── Strategies ──


class StrategyOut(BaseModel):
    id: int
    name: str
    category_id: int
    description: str
    applicable_to: list[str]
    estimated_savings: str | None = None
    complexity: str
    requirements: str | None = None
    example: str | None = None
    caveats: str | None = None
    related_item_ids: list[int]
    is_active: bool

    model_config = {"from_attributes": True}


class StrategyCreate(BaseModel):
    name: str
    category_id: int
    description: str
    applicable_to: list[str] = []
    estimated_savings: str | None = None
    complexity: str = "medium"
    requirements: str | None = None
    example: str | None = None
    caveats: str | None = None
    related_item_ids: list[int] = []


# ── User Items ──


class UserItemOut(BaseModel):
    id: int
    user_id: UUID
    item_id: int
    notes: str | None = None
    estimated_savings: float | None = None
    claimed: bool
    tax_year: int
    created_at: datetime
    item: ItemOut | None = None

    model_config = {"from_attributes": True}


class UserItemCreate(BaseModel):
    item_id: int
    notes: str | None = None
    estimated_savings: float | None = None
    claimed: bool = False
    tax_year: int = 2025


class UserItemUpdate(BaseModel):
    notes: str | None = None
    estimated_savings: float | None = None
    claimed: bool | None = None
    tax_year: int | None = None


# ── Search ──


class SearchRequest(BaseModel):
    query: str
    category_id: int | None = None
    deduction_type: str | None = None
    limit: int = 20


class SearchResult(BaseModel):
    items: list[ItemOut]
    total: int
    query: str


# ── Transactions ──


class TransactionOut(BaseModel):
    id: int
    date: datetime
    description: str
    amount: float
    merchant: str | None = None
    plaid_category: str | None = None
    tax_category_id: int | None = None
    is_deductible: bool | None = None
    notes: str | None = None
    source: str
    tax_year: int

    model_config = {"from_attributes": True}


class TransactionUpdate(BaseModel):
    tax_category_id: int | None = None
    is_deductible: bool | None = None
    notes: str | None = None


class CSVUploadResult(BaseModel):
    imported: int
    skipped: int
    errors: list[str]


# ── Tax Records ──


class TaxRecordOut(BaseModel):
    id: int
    tax_year: int
    filing_type: str
    form_type: str
    data: dict
    status: str
    generated_at: datetime

    model_config = {"from_attributes": True}


class TaxRecordCreate(BaseModel):
    tax_year: int
    filing_type: str
    form_type: str


# ── Analysis ──


class SynergyRequest(BaseModel):
    item_ids: list[int]


class SynergyResponse(BaseModel):
    analysis: str
    item_ids: list[int]
    cached: bool = False


class QuestionnaireStart(BaseModel):
    tax_year: int = 2025


class QuestionnaireAnswer(BaseModel):
    session_id: str
    question_key: str
    response: str


class DiscoveredItem(BaseModel):
    id: int
    name: str
    description: str | None = None


class QuestionnaireQuestion(BaseModel):
    session_id: str
    question_key: str
    question: str
    options: list[str] | None = None
    discovered_items: list[DiscoveredItem] = []
    is_final: bool = False


# ── Plaid ──


class PlaidLinkTokenResponse(BaseModel):
    link_token: str


class PlaidExchangeRequest(BaseModel):
    public_token: str
    institution_name: str
    institution_id: str | None = None


class PlaidConnectionOut(BaseModel):
    id: int
    institution_name: str
    institution_id: str | None = None
    last_synced: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
