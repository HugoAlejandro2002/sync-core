from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.domain.enums import TransactionSourceType, TransactionStatus
from app.domain.money import to_money
from app.models.management import Management
from app.models.transaction import Transaction
from app.repositories.management_repository import ManagementRepository
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction_schema import (
    ManualTransactionCreate,
    RejectTransactionResponse,
    TransactionMutationResponse,
    TransactionUpdate,
)
from app.services.management_service import recalculate_management
from app.services.response_builder import (
    build_financial_summary_short,
    build_transaction_response,
)


class TransactionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.tx_repo = TransactionRepository(session)
        self.mgmt_repo = ManagementRepository(session)

    async def _get_management(self, management_id: str) -> Management:
        management = await self.mgmt_repo.get_by_id(management_id)
        if management is None:
            raise NotFoundError(message="No se encontró la solicitud.")
        return management

    async def _get_transaction(self, transaction_id: str) -> Transaction:
        tx = await self.tx_repo.get_by_id(transaction_id)
        if tx is None:
            raise NotFoundError(message="No se encontró la transacción.")
        return tx

    async def add_manual(
        self, management_id: str, payload: ManualTransactionCreate
    ) -> TransactionMutationResponse:
        management = await self._get_management(management_id)
        tx = Transaction(
            management_id=management.id,
            customer_id=management.customer_id,
            media_asset_id=None,
            source_type=TransactionSourceType.MANUAL.value,
            transaction_type=payload.transaction_type,
            amount=to_money(payload.amount),
            currency=payload.currency,
            description=payload.description,
            transaction_date=payload.transaction_date,
            payment_method=payload.payment_method,
            evidence_text=None,
            confidence_score=None,
            status=TransactionStatus.MANUAL.value,
        )
        await self.tx_repo.create_manual(tx)
        await recalculate_management(self.session, management)
        await self.session.commit()
        await self.session.refresh(tx)
        return TransactionMutationResponse(
            transaction=build_transaction_response(tx),
            financial_summary=build_financial_summary_short(management),
        )

    async def update_transaction(
        self, transaction_id: str, payload: TransactionUpdate
    ) -> TransactionMutationResponse:
        tx = await self._get_transaction(transaction_id)
        data = payload.model_dump(exclude_unset=True)

        if "transaction_type" in data and data["transaction_type"] is not None:
            tx.transaction_type = data["transaction_type"]
        if "amount" in data and data["amount"] is not None:
            tx.amount = to_money(data["amount"])
        if "description" in data:
            tx.description = data["description"]
        if "transaction_date" in data:
            tx.transaction_date = data["transaction_date"]
        if "payment_method" in data and data["payment_method"] is not None:
            tx.payment_method = data["payment_method"]

        if tx.source_type == TransactionSourceType.AI.value:
            tx.status = TransactionStatus.CORRECTED.value

        await self.tx_repo.update(tx)
        management = await self._get_management(tx.management_id)
        await recalculate_management(self.session, management)
        await self.session.commit()
        await self.session.refresh(tx)
        return TransactionMutationResponse(
            transaction=build_transaction_response(tx),
            financial_summary=build_financial_summary_short(management),
        )

    async def reject_transaction(self, transaction_id: str) -> RejectTransactionResponse:
        tx = await self._get_transaction(transaction_id)
        await self.tx_repo.reject(tx)
        management = await self._get_management(tx.management_id)
        await recalculate_management(self.session, management)
        await self.session.commit()
        return RejectTransactionResponse(
            transaction_id=tx.id,
            financial_summary=build_financial_summary_short(management),
        )
