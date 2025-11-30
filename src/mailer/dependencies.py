from functools import lru_cache
from typing import Annotated

from fastapi.params import Depends

from src.mailer.smtp import MailerService
from src.config import SMTPSettingsDep

@lru_cache
def get_mailer_service(settings: SMTPSettingsDep) -> MailerService:
    return MailerService(settings)

MailerServiceDep = Annotated[MailerService, Depends(get_mailer_service)]