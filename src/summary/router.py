from fastapi import APIRouter

from src.database import DatabaseSession
from src.summary.models import SummaryResponse
from src.summary.services import SummaryServices


router = APIRouter(prefix="/summary", tags=["Summary"])

@router.get("/{schema}", response_model=SummaryResponse)
async def get_summary_endpoint(schema: str, database: DatabaseSession) -> SummaryResponse:
    return (await SummaryServices.get(database=database, schema=schema)).model_dump()


