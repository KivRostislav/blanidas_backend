from fastapi import BackgroundTasks
from sqlalchemy import text

from src.database import DatabaseSession
from src.event import emit, EventTypes
from src.health_check.models import HealthCheckResponse, HealthCheckResponseStatus
from src.mailer.smtp import MailerService


class HealthCheckServices:
    @staticmethod
    async def check_health(
            database: DatabaseSession,
            background_tasks: BackgroundTasks,
            superuser_email: str,
            mailer: MailerService,
    ):
        try:
            await database.execute(text("SELECT 1"))
            await emit(
                EventTypes.health_check,
                background_tasks,
                to=superuser_email,
                mailer=mailer
            )
        except Exception:
            return HealthCheckResponse(status=HealthCheckResponseStatus.error)

        return HealthCheckResponse(status=HealthCheckResponseStatus.ok)
