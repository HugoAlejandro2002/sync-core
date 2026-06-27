from __future__ import annotations

from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.management import Management


class ManagementRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, management: Management) -> Management:
        self.session.add(management)
        await self.session.flush()
        return management

    async def get_by_id(self, management_id: str) -> Management | None:
        stmt = (
            select(Management)
            .where(Management.id == management_id)
            .options(
                selectinload(Management.customer),
                selectinload(Management.media_assets),
                selectinload(Management.transactions),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, status: str | None = None) -> list[Management]:
        stmt = (
            select(Management)
            .options(
                selectinload(Management.customer),
                selectinload(Management.media_assets),
            )
            .order_by(Management.submitted_at.desc())
        )
        if status and status != "all":
            stmt = stmt.where(Management.status == status)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(Management))
        return int(result.scalar_one())

    async def update_status(self, management: Management, status: str) -> None:
        management.status = status
        await self.session.flush()

    async def update_advisor_notes(self, management: Management, advisor_notes: str | None) -> None:
        management.advisor_notes = advisor_notes
        await self.session.flush()

    async def update_totals(
        self,
        management: Management,
        *,
        total_income: Decimal,
        total_expense: Decimal,
        net_balance: Decimal,
        confidence_score: Decimal | None,
    ) -> None:
        management.total_income = total_income
        management.total_expense = total_expense
        management.net_balance = net_balance
        management.confidence_score = confidence_score
        await self.session.flush()

    async def update_analysis(
        self,
        management: Management,
        *,
        analysis_summary: dict[str, Any] | None,
        alerts: list[dict[str, Any]] | None,
    ) -> None:
        management.analysis_summary = analysis_summary
        management.alerts = alerts
        await self.session.flush()
