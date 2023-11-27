from pydantic import BaseModel, EmailStr


class SendMailPayload(BaseModel):
    # from_addr: EmailStr
    to_addrs: list[EmailStr]
    cc: list[EmailStr] | None = None
    bcc: list[EmailStr] | None = None
    subject: str | None = None
    text: str
