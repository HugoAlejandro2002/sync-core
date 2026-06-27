from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.domain.uploads import UploadedFile
from app.schemas.management_schema import (
    AdvisorNotesResponse,
    AdvisorNotesUpdate,
    ManagementCreateInput,
    ManagementDetail,
    ManagementListResponse,
    StatusResponse,
    StatusUpdate,
)
from app.services.evidence_processing_service import EvidenceProcessingService
from app.services.management_service import ManagementService

router = APIRouter(prefix="/api/v1/managements", tags=["managements"])


async def _to_uploaded_files(files: list[UploadFile]) -> list[UploadedFile]:
    uploaded: list[UploadedFile] = []
    for file in files:
        uploaded.append(
            UploadedFile(
                filename=file.filename or "evidencia",
                content_type=file.content_type or "application/octet-stream",
                content=await file.read(),
            )
        )
    return uploaded


@router.post("", response_model=ManagementDetail, status_code=201)
async def create_management(
    full_name: str = Form(..., min_length=1),
    requested_amount: Decimal = Form(..., gt=0),
    phone_number: str | None = Form(None),
    nit: str | None = Form(None),
    business_name: str | None = Form(None),
    business_type: str | None = Form(None),
    business_description: str | None = Form(None),
    market_location: str | None = Form(None),
    currency: str = Form("BOB"),
    visit_date: date | None = Form(None),
    advisor_notes: str | None = Form(None),
    files: list[UploadFile] = File(default=[]),
    session: AsyncSession = Depends(get_session),
) -> ManagementDetail:
    data = ManagementCreateInput(
        full_name=full_name,
        phone_number=phone_number,
        nit=nit,
        business_name=business_name,
        business_type=business_type,
        business_description=business_description,
        market_location=market_location,
        requested_amount=requested_amount,
        currency=currency,
        visit_date=visit_date,
        advisor_notes=advisor_notes,
    )
    uploaded = await _to_uploaded_files(files)
    return await ManagementService(session).create_management(data, uploaded)


@router.get("", response_model=ManagementListResponse)
async def list_managements(
    status: str = "all",
    session: AsyncSession = Depends(get_session),
) -> ManagementListResponse:
    return await ManagementService(session).list_managements(status)


@router.get("/{management_id}", response_model=ManagementDetail)
async def get_management(
    management_id: str,
    session: AsyncSession = Depends(get_session),
) -> ManagementDetail:
    return await ManagementService(session).get_management_detail(management_id)


@router.post("/{management_id}/evidence", response_model=ManagementDetail)
async def add_evidence(
    management_id: str,
    files: list[UploadFile] = File(...),
    session: AsyncSession = Depends(get_session),
) -> ManagementDetail:
    uploaded = await _to_uploaded_files(files)
    return await EvidenceProcessingService.from_session(session).add_evidence_to_management(
        management_id, uploaded
    )


@router.patch("/{management_id}/advisor-notes", response_model=AdvisorNotesResponse)
async def update_advisor_notes(
    management_id: str,
    payload: AdvisorNotesUpdate,
    session: AsyncSession = Depends(get_session),
) -> AdvisorNotesResponse:
    return await ManagementService(session).update_advisor_notes(
        management_id, payload.advisor_notes
    )


@router.patch("/{management_id}/status", response_model=StatusResponse)
async def update_status(
    management_id: str,
    payload: StatusUpdate,
    session: AsyncSession = Depends(get_session),
) -> StatusResponse:
    return await ManagementService(session).update_status(management_id, payload.status)
