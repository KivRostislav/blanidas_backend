from email.message import EmailMessage
from smtplib import SMTP
from typing import Any
from jinja2 import Environment, FileSystemLoader

from src.config import SMTPSettings, MailTemplate

class MailerService:
    def __init__(self, settings: SMTPSettings) -> None:
        self.env = Environment(loader=FileSystemLoader(settings.templates_dir))
        self.settings = settings

    def send_message(self, template: MailTemplate, to: str, payload: dict[str, Any]) -> None:
        content = self.env.get_template(template.content_file).render(**payload)
        subject = self.env.get_template(template.subject_file).render(**payload)
        msg = EmailMessage()
        msg['Subject'] = subject.strip()
        msg['From'] = self.settings.from_address
        msg['To'] = "kivrostislav951@gmail.com"
        msg.set_content(content, subtype='html')

        conn = SMTP(self.settings.server, self.settings.port)
        conn.starttls()

        conn.login(self.settings.username, self.settings.password)

        try:
            conn.send_message(msg)
        finally:
            conn.quit()