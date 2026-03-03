from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tax_shield.config import settings
from tax_shield.models.db_models import PlaidConnection, Transaction
from tax_shield.security import decrypt_field, encrypt_field


async def create_link_token(user_id: UUID) -> str:
    """Create a Plaid Link token for the frontend."""
    import plaid
    from plaid.api import plaid_api
    from plaid.model.country_code import CountryCode
    from plaid.model.link_token_create_request import LinkTokenCreateRequest
    from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
    from plaid.model.products import Products

    configuration = plaid.Configuration(
        host=_get_plaid_host(),
        api_key={"clientId": settings.PLAID_CLIENT_ID, "secret": settings.PLAID_SECRET},
    )
    api_client = plaid.ApiClient(configuration)
    client = plaid_api.PlaidApi(api_client)

    request = LinkTokenCreateRequest(
        user=LinkTokenCreateRequestUser(client_user_id=str(user_id)),
        client_name="Tax Shield",
        products=[Products("transactions")],
        country_codes=[CountryCode("US")],
        language="en",
    )
    response = client.link_token_create(request)
    return response.link_token


async def exchange_public_token(
    db: AsyncSession,
    user_id: UUID,
    public_token: str,
    institution_name: str,
    institution_id: str | None,
) -> PlaidConnection:
    """Exchange public token for access token and store connection."""
    import plaid
    from plaid.api import plaid_api
    from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest

    configuration = plaid.Configuration(
        host=_get_plaid_host(),
        api_key={"clientId": settings.PLAID_CLIENT_ID, "secret": settings.PLAID_SECRET},
    )
    api_client = plaid.ApiClient(configuration)
    client = plaid_api.PlaidApi(api_client)

    request = ItemPublicTokenExchangeRequest(public_token=public_token)
    response = client.item_public_token_exchange(request)

    connection = PlaidConnection(
        user_id=user_id,
        access_token_encrypted=encrypt_field(response.access_token),
        institution_name=institution_name,
        institution_id=institution_id,
    )
    db.add(connection)
    await db.commit()
    await db.refresh(connection)
    return connection


async def sync_transactions(
    db: AsyncSession,
    connection: PlaidConnection,
) -> int:
    """Sync transactions from Plaid for a connection."""
    import plaid
    from plaid.api import plaid_api
    from plaid.model.transactions_sync_request import TransactionsSyncRequest

    access_token = decrypt_field(connection.access_token_encrypted)

    configuration = plaid.Configuration(
        host=_get_plaid_host(),
        api_key={"clientId": settings.PLAID_CLIENT_ID, "secret": settings.PLAID_SECRET},
    )
    api_client = plaid.ApiClient(configuration)
    client = plaid_api.PlaidApi(api_client)

    request = TransactionsSyncRequest(
        access_token=access_token,
        cursor=connection.cursor or "",
    )
    response = client.transactions_sync(request)

    imported = 0
    for txn in response.added:
        # Skip if already exists
        existing = await db.execute(
            select(Transaction).where(Transaction.plaid_transaction_id == txn.transaction_id)
        )
        if existing.scalar_one_or_none():
            continue

        transaction = Transaction(
            user_id=connection.user_id,
            plaid_connection_id=connection.id,
            date=datetime.combine(txn.date, datetime.min.time()).replace(tzinfo=UTC),
            description=txn.name or txn.merchant_name or "",
            amount=abs(txn.amount),
            merchant=txn.merchant_name,
            plaid_category=", ".join(txn.category) if txn.category else None,
            source="plaid",
            tax_year=txn.date.year,
            plaid_transaction_id=txn.transaction_id,
        )
        db.add(transaction)
        imported += 1

    # Update cursor
    connection.cursor = response.next_cursor
    connection.last_synced = datetime.now(UTC)
    await db.commit()

    return imported


def _get_plaid_host() -> str:
    import plaid

    env_map = {
        "sandbox": plaid.Environment.Sandbox,
        "development": plaid.Environment.Development,
        "production": plaid.Environment.Production,
    }
    return env_map.get(settings.PLAID_ENV, plaid.Environment.Sandbox)
