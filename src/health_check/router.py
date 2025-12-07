from fastapi import APIRouter, BackgroundTasks

from src.config import SettingsDep
from src.database import DatabaseSession
from src.failure_type.services import FailureTypeServices
from src.health_check.services import HealthCheckServices
from src.health_check.models import HealthCheckResponse
from src.mailer.dependencies import MailerServiceDep

router = APIRouter(prefix="/health-check", tags=["Health Check"])
services = FailureTypeServices()

@router.get("/", response_model=HealthCheckResponse)
async def get_health_check_endpoint(
        database: DatabaseSession,
        background_tasks: BackgroundTasks,
        mailer: MailerServiceDep,
        settings: SettingsDep,
) -> HealthCheckResponse:
    return await HealthCheckServices.check_health(
        database=database,
        background_tasks=background_tasks,
        superuser_email=settings.superuser_email,
        mailer=mailer
    )
