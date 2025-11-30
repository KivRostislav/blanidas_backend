from src.event import EventTypes, on
from src.mailer.models import LowStockMessagePayload
from src.mailer.smtp import MailerService


@on(EventTypes.low_stock.value)
def on_low_stock(to: str, mailer: MailerService, payload: LowStockMessagePayload):
    mailer.send_message(
        template=mailer.settings.low_stock_template,
        to=to,
        payload=payload.model_dump()
    )