from typing import List, Optional
from enum import Enum
from datetime import datetime

from pydantic import BaseModel, EmailStr

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.header import decode_header
from email import encoders


class MessagePriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"

class EmailAttachment(BaseModel):
    filename: str
    content: bytes
    content_type: str = "application/octet-stream"

class EmailMessage(BaseModel):
    subject: str
    body: str
    recipients: List[EmailStr]
    message_id: Optional[str] = None
    
    sender: EmailStr
    cc: List[EmailStr] = []
    bcc: List[EmailStr] = []
    reply_to: Optional[EmailStr] = None

    in_reply_to: Optional[str] = None
    references: Optional[str] = None
    
    timestamp: datetime = datetime.now()
    priority: MessagePriority = MessagePriority.NORMAL

    html_body: Optional[str] = None
    attachments: List[EmailAttachment] = []

    is_read: bool = False
    is_important: bool = False

    def to_mime_message(self):
        priority_map = {
            MessagePriority.HIGH: "1",
            MessagePriority.NORMAL: "3", 
            MessagePriority.LOW: "5"
        }

        email_message = MIMEMultipart()
        email_message['From'] = self.sender
        email_message['To'] = ', '.join(self.recipients)
        email_message['Subject'] = self.subject
        
        if self.cc:
            email_message['Cc'] = ', '.join(self.cc)
        if self.bcc:
            email_message['Bcc'] = ', '.join(self.bcc)
        if self.reply_to:
            email_message['Reply-To'] = self.reply_to
        
        email_message['X-Priority'] = priority_map.get(self.priority, "3")
        
        email_message.attach(MIMEText(self.body, 'plain'))
        
        if self.html_body:
            email_message.attach(MIMEText(self.html_body, 'html'))
        
        for attachment in self.attachments:
            part = MIMEBase(*attachment.content_type.split('/', 1))
            part.set_payload(attachment.content)
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={attachment.filename}'
            )
            email_message.attach(part)

        return email_message

    @staticmethod
    def from_mime_message(message):
        subject, encoding = decode_header(message["Subject"])[0]

        if isinstance(subject, bytes):
            subject = subject.decode(encoding if encoding else 'utf-8')
        
        sender = message.get("From", "")
        
        body = ""
        html_body = None
        
        if message.is_multipart():
            for part in message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if "attachment" not in content_disposition:
                    if content_type == "text/plain":
                        body = part.get_payload(decode=True).decode()
                    elif content_type == "text/html":
                        html_body = part.get_payload(decode=True).decode()
        else:
            body = message.get_payload(decode=True).decode()
        
        date_str = message.get("Date", "")
        timestamp = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")

        return EmailMessage(
            subject=subject or "Без темы",
            body=body or "",
            recipients=[message['To'],],
            sender=sender,
            timestamp=timestamp,
            html_body=html_body
        )

class SMTPConfig(BaseModel):
    server: str
    port: int = 465
    username: str
    password: str

class IMAPConfig(BaseModel):
    server: str
    port: int = 993
    username: str
    password: str