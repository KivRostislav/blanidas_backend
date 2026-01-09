from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.auth.dependencies import allowed
from src.auth.schemas import Role
from src.database import DatabaseSession
from src.statistics.models import StatisticsTimeStep, TimeFrame, StatisticsResponse
from src.statistics.services import StatisticsServices


router = APIRouter(prefix="/statistics", tags=["Statistics"])

def get_timeframe(
        from_date: datetime = Query(default=datetime.min),
        to_date: datetime = Query(default=datetime.today()),
        step: StatisticsTimeStep = Query(default=StatisticsTimeStep.month),
) -> TimeFrame:
    return TimeFrame(
        from_date=from_date,
        to_date=to_date,
        step=step,
    )

@router.get("/", response_model=StatisticsResponse)
async def get_statistics_endpoint(
        database: DatabaseSession,
        timeframe: Annotated[TimeFrame, Depends(get_timeframe)],
        _: Annotated[None, Depends(allowed(role=Role.manager))]
) -> StatisticsResponse:
    return await StatisticsServices.get(database=database, data=timeframe.model_dump())

