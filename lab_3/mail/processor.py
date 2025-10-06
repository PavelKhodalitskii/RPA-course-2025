from typing import List, Optional
import email as email_lib

import smtplib
import imaplib

from .models import SMTPConfig, IMAPConfig, EmailMessage


class MailProcessor:
    def __init__(self, smtp_config: SMTPConfig, imap_config: Optional[IMAPConfig]):
        self.smtp_config = smtp_config
        self.imap_config = imap_config
        self.received_messages = []

        self.smtp_server = smtplib.SMTP_SSL(self.smtp_config.server, self.smtp_config.port)
        self.smtp_server.login(self.smtp_config.username, self.smtp_config.password)

        self.imap_server = imaplib.IMAP4_SSL(self.imap_config.server, self.imap_config.port)
        self.imap_server.login(self.imap_config.username, self.imap_config.password)

    def send_message(self, message: EmailMessage):
        all_recipients = message.recipients + message.cc + message.bcc

        mime_message = message.to_mime_message()

        try:
            self.smtp_server.sendmail(message.sender, all_recipients, mime_message.as_string())
        except Exception as e:
            print(f"Ошиька при отправке сообщения {message}: {e}")
    
    def get_messages(self, folder: str = "inbox", filter_func = None, count: int = 10) -> List[EmailMessage]:
        try:
            messages = self._fetch_imap_messages(folder, count)

            if filter_func:
                messages = [msg for msg in messages if filter_func(msg)]
            
            messages.sort(key=lambda x: x.timestamp, reverse=True)
            return messages
        except Exception as e:
            print(e)
            return None
    
    def _fetch_imap_messages(self, folder: str = "inbox", count: int = 10) -> List[EmailMessage]:
        try:
            self.imap_server.select(folder)
            
            _, messages = self.imap_server.search(None, 'ALL')
            email_ids = messages[0].split()
            
            recent_email_ids = email_ids[-count:] if len(email_ids) > count else email_ids
            recent_email_ids.reverse()
            
            fetched_messages = []
            
            for email_id in recent_email_ids:
                _, msg_data = self.imap_server.fetch(email_id, '(RFC822)')
                
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email_lib.message_from_bytes(response_part[1])
                        
                        fetched_messages.append(EmailMessage.from_mime_message(msg))

            self.imap_server.close()
            return fetched_messages
            
        except Exception as e:
            print(f"Ошибка при получении писем через IMAP: {e}")
            
        self.imap_server.close()
        return []

    def quit(self):
        self.smtp_server.quit()
        self.imap_server.logout()
    