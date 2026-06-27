from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.transaction_schema import (
    ManualTransactionCreate,
    RejectTransactionResponse,
    TransactionMutationResponse,
    TransactionUpdate,
)
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/api/v1", tags=["transactions"])


@router.post(
    "/managements/{management_id}/transactions",
    response_model=TransactionMutationResponse,
    status_code=201,
)
async def add_manual_transaction(
    management_id: str,
    payload: ManualTransactionCreate,
    session: AsyncSession = Depends(get_session),
) -> TransactionMutationResponse:
    return await TransactionService(session).add_manual(management_id, payload)


@router.patch("/transactions/{transaction_id}", response_model=TransactionMutationResponse)
async def update_transaction(
    transaction_id: str,
    payload: TransactionUpdate,
    session: AsyncSession = Depends(get_session),
) -> TransactionMutationResponse:
    return await TransactionService(session).update_transaction(transaction_id, payload)


@router.post(
    "/transactions/{transaction_id}/reject",
    response_model=RejectTransactionResponse,
)
async def reject_transaction(
    transaction_id: str,
    session: AsyncSession = Depends(get_session),
) -> RejectTransactionResponse:
    return await TransactionService(session).reject_transaction(transaction_id)
