from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import TransactionStatus
from app.models.transaction import Transaction


class TransactionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_many(self, transactions: list[Transaction]) -> list[Transaction]:
        if not transactions:
            return []
        self.session.add_all(transactions)
        await self.session.flush()
        return transactions

    async def create_manual(self, transaction: Transaction) -> Transaction:
        self.session.add(transaction)
        await self.session.flush()
        return transaction

    async def get_by_id(self, transaction_id: str) -> Transaction | None:
        return await self.session.get(Transaction, transaction_id)

    async def list_by_management(self, management_id: str) -> list[Transaction]:
        stmt = (
            select(Transaction)
            .where(Transaction.management_id == management_id)
            .order_by(Transaction.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_summary_by_management(self, management_id: str) -> list[Transaction]:
        """Non-rejected transactions used for totals/confidence calculations."""
        stmt = select(Transaction).where(
            Transaction.management_id == management_id,
            Transaction.status != TransactionStatus.REJECTED.value,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, transaction: Transaction) -> None:
        await self.session.flush()

    async def reject(self, transaction: Transaction) -> None:
        transaction.status = TransactionStatus.REJECTED.value
        await self.session.flush()
