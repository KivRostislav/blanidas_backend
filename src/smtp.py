from dataclasses import dataclass
from email.message import EmailMessage
from enum import Enum
from pathlib import Path
from smtplib import SMTP
from typing import Any

from src.config import SMTPSettings
from src.exception import TemplateFileNotFoundError


class MessageTemplate:
    def __init__(self, subject: str, content: str):
        self.content = content
        self.subject = subject

class MessageType(str, Enum):
    low_stock = "low_stock"
    repair_request_creation = "repair_request_creation"

templates: dict[MessageType, MessageTemplate] = {}

def initialize_templates(settings: SMTPSettings) -> None:
    global templates
#sdfdsfsdfsdfdfds    sdfffffffffffffffffffffffffffffff
    missing_files = []
    if not Path(settings.low_stock_template_file).exists():
        missing_files.append(settings.low_stock_template_file)
    if not Path(settings.repair_request_creation_template_file).exists():
        missing_files.append(settings.repair_request_creation_template_file)
    if missing_files:
        raise TemplateFileNotFoundError(missing_files)

    with open(settings.low_stock_template_file, "r") as file:
        subject = file.readline().strip()
        content = file.read().strip()
        templates[MessageType.low_stock] = MessageTemplate(subject, content)

    with open(settings.low_stock_template_file, "r") as file:
        subject = file.readline().strip()
        content = file.read().strip()
        templates[MessageType.repair_request_creation] = MessageTemplate(subject, content)

@dataclass
class LowStockMessagePayload:
    receiver_username: str

    spare_part_name: str
    spare_part_serial_number: str

    spare_part_current_quantity: int
    spare_part_min_quantity: int


def send_message(message_type: MessageType, to: str, payload: dict[str, Any], settings: SMTPSettings) -> None:
    msg = EmailMessage()
    msg['Subject'] = "subject"
    msg['From'] = settings.from_address
    msg['To'] = "kivrostislav951@gmail.com"  # dsfdsfdsfsddsfdfdsfsdfdsf
    content = templates[MessageType.low_stock].content
    msg.set_content(content, subtype='html')

    conn = SMTP(settings.server, settings.port)
    conn.starttls()

    conn.login(settings.username, settings.password)

    try:
        conn.send_message(msg)
    finally:
        conn.quit()