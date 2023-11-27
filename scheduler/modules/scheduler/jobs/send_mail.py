import smtplib
from email.message import EmailMessage

from dependency_injector.wiring import inject, Provide

from .schemas import SendMailPayload


@inject
def send_email(mail_config=Provide["config.mail"], **kwargs):
    payload = SendMailPayload.parse_obj(kwargs)
    email_message = EmailMessage()
    email_message.set_charset('utf-8')
    # email_message["From"] = payload.from_addr
    email_message["From"] = mail_config["from_addr"]
    email_message["To"] = payload.to_addrs
    email_message["Subject"] = payload.subject
    if payload.cc:
        email_message["Cc"] = payload.cc
    if payload.bcc:
        email_message["Bcc"] = payload.bcc
    email_message.add_alternative(payload.text, "html")

    with smtplib.SMTP(host=mail_config["host"], port=mail_config["port"]) as smtp:
        smtp.send_message(email_message)
