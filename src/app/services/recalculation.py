from sqlalchemy.ext.asyncio import AsyncSession

from app.models.management import Management
from app.repositories.management_repository import ManagementRepository
from app.repositories.media_asset_repository import MediaAssetRepository
from app.repositories.transaction_repository import TransactionRepository
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
