from __future__ import annotations

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidStatusError, NotFoundError
from app.domain.enums import ManagementStatus
from app.domain.labels import management_status_label
from app.domain.money import to_money
from app.models.customer import Customer
from app.models.management import Management
from app.repositories.customer_repository import CustomerRepository
from app.repositories.management_repository import ManagementRepository
from app.repositories.media_asset_repository import MediaAssetRepository
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.management_schema import (
    AdvisorNotesResponse,
    ManagementCreateInput,
    ManagementDetail,
    ManagementListResponse,
    StatusResponse,
)
from app.services.response_builder import (
    build_management_detail,
    build_management_list_item,
)
from app.services.summary_service import SummaryResult, SummaryService


async def recalculate_management(session: AsyncSession, management: Management) -> SummaryResult:
    """Recompute totals/analysis/alerts from fresh transaction + media data and persist them."""
    transactions = await TransactionRepository(session).list_by_management(management.id)
    media_assets = await MediaAssetRepository(session).list_by_management(management.id)

    result = SummaryService().calculate(transactions, media_assets)

    mgmt_repo = ManagementRepository(session)
    await mgmt_repo.update_totals(
        management,
        total_income=result.total_income,
        total_expense=result.total_expense,
        net_balance=result.net_balance,
        confidence_score=result.confidence_score,
    )
    await mgmt_repo.update_analysis(
        management,
        analysis_summary=result.analysis_summary,
        alerts=result.alerts,
    )
    return result


class ManagementService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.customer_repo = CustomerRepository(session)
        self.mgmt_repo = ManagementRepository(session)

    async def create_management(self, data: ManagementCreateInput) -> ManagementDetail:
        customer = Customer(
            full_name=data.full_name,
            phone_number=data.phone_number,
            nit=data.nit,
            business_name=data.business_name,
            business_type=data.business_type,
            business_description=data.business_description,
            market_location=data.market_location,
        )
        await self.customer_repo.create(customer)

        application_code = f"APP-{await self.mgmt_repo.count() + 1:03d}"
        management = Management(
            customer_id=customer.id,
            application_code=application_code,
            requested_amount=to_money(data.requested_amount),
            currency=data.currency,
            status=ManagementStatus.PENDING.value,
            submitted_at=datetime.now(),
            visit_date=data.visit_date,
            advisor_notes=data.advisor_notes,
        )
        await self.mgmt_repo.create(management)
        await recalculate_management(self.session, management)
        await self.session.commit()

        return await self.get_management_detail(management.id)

    async def list_managements(self, status: str | None = None) -> ManagementListResponse:
        managements = await self.mgmt_repo.list(status)
        return ManagementListResponse(items=[build_management_list_item(m) for m in managements])

    async def get_management_detail(self, management_id: str) -> ManagementDetail:
        management = await self.mgmt_repo.get_by_id(management_id)
        if management is None:
            raise NotFoundError(message="No se encontró la solicitud.")
        return build_management_detail(management)

    async def update_advisor_notes(
        self, management_id: str, advisor_notes: str | None
    ) -> AdvisorNotesResponse:
        management = await self.mgmt_repo.get_by_id(management_id)
        if management is None:
            raise NotFoundError(message="No se encontró la solicitud.")
        await self.mgmt_repo.update_advisor_notes(management, advisor_notes)
        await self.session.commit()
        return AdvisorNotesResponse(
            management_id=management.id, advisor_notes=management.advisor_notes
        )

    async def update_status(self, management_id: str, status: str) -> StatusResponse:
        if status not in {s.value for s in ManagementStatus}:
            raise InvalidStatusError()
        management = await self.mgmt_repo.get_by_id(management_id)
        if management is None:
            raise NotFoundError(message="No se encontró la solicitud.")
        await self.mgmt_repo.update_status(management, status)
        await self.session.commit()
        return StatusResponse(
            management_id=management.id,
            status=management.status,
            status_label=management_status_label(management.status),
        )
