from __future__ import annotations

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidStatusError, NotFoundError
from app.domain.enums import ManagementStatus
from app.domain.labels import management_status_label
from app.domain.money import to_money
from app.domain.uploads import UploadedFile
from app.models.customer import Customer
from app.models.management import Management
from app.repositories.customer_repository import CustomerRepository
from app.repositories.management_repository import ManagementRepository
from app.schemas.management_schema import (
    AdvisorNotesResponse,
    ManagementCreateInput,
    ManagementDetail,
    ManagementListResponse,
    StatusResponse,
)
from app.services.recalculation import recalculate_management
from app.services.response_builder import (
    build_management_detail,
    build_management_list_item,
)


class ManagementService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.customer_repo = CustomerRepository(session)
        self.mgmt_repo = ManagementRepository(session)

    async def create_management(
        self, data: ManagementCreateInput, files: list[UploadedFile] | None = None
    ) -> ManagementDetail:
        # Lazy import avoids loading OpenCV/AI deps unless files are processed.
        from app.services.evidence_processing_service import EvidenceProcessingService

        files = files or []
        if files:
            EvidenceProcessingService.validate_files(files)

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

        if files:
            evidence = EvidenceProcessingService.from_session(self.session)
            await evidence.process_files(management, files)

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
