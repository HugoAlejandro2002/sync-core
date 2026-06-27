from __future__ import annotations

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import AppError, NotFoundError, ValidationError
from app.domain.enums import MediaAssetStatus, TransactionSourceType, TransactionStatus
from app.domain.labels import document_type_label
from app.domain.money import to_money
from app.domain.uploads import UploadedFile
from app.models.management import Management
from app.models.media_asset import MediaAsset
from app.models.transaction import Transaction
from app.providers.storage.base import StorageProvider
from app.providers.storage.local_storage_provider import LocalStorageProvider
from app.repositories.management_repository import ManagementRepository
from app.repositories.media_asset_repository import MediaAssetRepository
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.extraction_schema import FinancialExtractionSchema
from app.schemas.management_schema import ManagementDetail
from app.services.ai_extraction_service import AIExtractionService, build_extraction_provider
from app.services.image_preprocessing_service import ImagePreprocessingService
from app.services.recalculation import recalculate_management
from app.services.response_builder import build_management_detail
from app.utils.dates import parse_iso_date
from app.utils.files import is_allowed_image

LOW_CONFIDENCE = Decimal("0.75")
_INVALID_IMAGE = "El archivo enviado no es una imagen válida."


def _to_confidence(value: float | None) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value)).quantize(Decimal("0.0001"))


def _failure_reason(exc: Exception) -> str:
    """Readable detail for a failed evidence, shown to the advisor.

    Our AppError subclasses don't forward their message to Exception, so ``str(exc)``
    is empty for them — the real cause (e.g. the Gemini/SDK error) lives in
    ``details['reason']``. Combine the Spanish message with that reason when present.
    """
    if isinstance(exc, AppError):
        reason = exc.details.get("reason")
        return f"{exc.message} {reason}".strip() if reason else exc.message
    return str(exc) or exc.__class__.__name__


class EvidenceProcessingService:
    """Stores, preprocesses, and AI-extracts evidence images into media assets + transactions."""

    def __init__(
        self,
        session: AsyncSession,
        storage: StorageProvider,
        preprocessor: ImagePreprocessingService,
        extraction_service: AIExtractionService,
    ) -> None:
        self.session = session
        self.storage = storage
        self.preprocessor = preprocessor
        self.extraction = extraction_service
        self.media_repo = MediaAssetRepository(session)
        self.tx_repo = TransactionRepository(session)
        self.mgmt_repo = ManagementRepository(session)

    @classmethod
    def from_session(cls, session: AsyncSession) -> EvidenceProcessingService:
        settings = get_settings()
        return cls(
            session=session,
            storage=LocalStorageProvider(settings.LOCAL_MEDIA_DIR),
            preprocessor=ImagePreprocessingService(),
            extraction_service=AIExtractionService(build_extraction_provider(settings)),
        )

    @staticmethod
    def validate_files(files: list[UploadedFile]) -> None:
        for file in files:
            if not is_allowed_image(file.content_type):
                raise ValidationError(message=_INVALID_IMAGE)

    async def add_evidence_to_management(
        self, management_id: str, files: list[UploadedFile]
    ) -> ManagementDetail:
        management = await self.mgmt_repo.get_by_id(management_id)
        if management is None:
            raise NotFoundError(message="No se encontró la solicitud.")
        await self.process_files(management, files)
        await recalculate_management(self.session, management)
        await self.session.commit()

        reloaded = await self.mgmt_repo.get_by_id(management_id)
        assert reloaded is not None
        return build_management_detail(reloaded)

    async def process_files(self, management: Management, files: list[UploadedFile]) -> None:
        """Append-only: never deletes prior evidence/transactions. One bad image is
        marked failed and the rest continue. Caller is responsible for recalc + commit."""
        self.validate_files(files)
        for file in files:
            await self._process_one(management, file)

    async def _process_one(self, management: Management, file: UploadedFile) -> None:
        original_path = await self.storage.save_bytes(
            file.content, file.filename, file.content_type, "original"
        )
        media = MediaAsset(
            management_id=management.id,
            customer_id=management.customer_id,
            original_filename=file.filename,
            mime_type=file.content_type,
            size_bytes=len(file.content),
            original_path=original_path,
            status=MediaAssetStatus.PROCESSING.value,
        )
        await self.media_repo.create(media)

        try:
            processed = await self.preprocessor.preprocess(file.content)
            processed_path = await self.storage.save_bytes(
                processed, file.filename, "image/png", "processed"
            )
            extraction = await self.extraction.extract(processed, file.content_type, file.filename)
            await self._apply_extraction(management, media, extraction, processed_path)
        except Exception as exc:  # noqa: BLE001 - isolate a single failing image
            await self.media_repo.mark_failed(media, error_message=_failure_reason(exc)[:500])

    async def _apply_extraction(
        self,
        management: Management,
        media: MediaAsset,
        extraction: FinancialExtractionSchema,
        processed_path: str,
    ) -> None:
        confidence = _to_confidence(extraction.confidence_score)
        status = (
            MediaAssetStatus.REVIEW.value
            if confidence is not None and confidence < LOW_CONFIDENCE
            else MediaAssetStatus.PROCESSED.value
        )
        await self.media_repo.update_processing_result(
            media,
            status=status,
            document_type=extraction.document_type,
            document_type_label=extraction.document_type_label
            or document_type_label(extraction.document_type),
            detected_amount=to_money(extraction.detected_amount)
            if extraction.detected_amount is not None
            else None,
            extracted_text=extraction.raw_text,
            confidence_score=confidence,
            ai_raw_response=extraction.model_dump(mode="json"),
            processed_path=processed_path,
        )

        transactions = [
            Transaction(
                management_id=management.id,
                customer_id=management.customer_id,
                media_asset_id=media.id,
                source_type=TransactionSourceType.AI.value,
                transaction_type=item.transaction_type,
                amount=to_money(item.amount),
                currency=item.currency,
                description=item.description,
                transaction_date=parse_iso_date(item.transaction_date),
                payment_method=item.payment_method,
                evidence_text=item.evidence_text,
                confidence_score=_to_confidence(item.confidence_score),
                status=TransactionStatus.EXTRACTED.value,
            )
            for item in extraction.transactions
        ]
        await self.tx_repo.create_many(transactions)
