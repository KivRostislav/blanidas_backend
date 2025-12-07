from src.event import EventTypes, on
from src.mailer.models import LowStockMessagePayload, RepairRequestCreatedMessagePayload
from src.mailer.smtp import MailerService


@on(EventTypes.low_stock.value)
def on_low_stock(to: str, mailer: MailerService, payload: LowStockMessagePayload):
    mailer.send_message(
        template=mailer.settings.low_stock_template,
        payload=payload.model_dump(),
        to=to,
    )

@on(EventTypes.repair_request_created.value)
def on_repair_request_created(to: str, mailer: MailerService, payload: RepairRequestCreatedMessagePayload):
    mailer.send_message(
        template=mailer.settings.repair_request_created_template,
        payload=payload.model_dump(),
        to=to,
    )

@on(EventTypes.health_check.value)
def on_health_check_created(to: str, mailer: MailerService):
    mailer.send_message(
        template=mailer.settings.health_check_template,
        payload={},
        to=to,
    )