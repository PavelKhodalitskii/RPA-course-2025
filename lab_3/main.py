from mail.models import SMTPConfig, IMAPConfig, EmailMessage, EmailAttachment
from mail import MailProcessor


if __name__ == "__main__":
    my_mail = "playground01@mail.ru"

    # Пароль не скажу!
    smtp_config = SMTPConfig(server="smtp.mail.ru", username=my_mail, password="")
    imap_config = IMAPConfig(server="imap.mail.ru", username=my_mail, password="")
    mail_processor = MailProcessor(smtp_config=smtp_config, imap_config=imap_config)

    message = EmailMessage(
        subject = "Тестовое сообщение 1",
        body="Ну чето короче там, ну в общем, ну знаешь, ну то самое",
        recipients=[my_mail,],
        sender=my_mail,
    )

    # Простое сообщение
    mail_processor.send_message(message=message)

    # С файлом
    with open("attachment.docx", "rb") as file:
        content_bytes = file.read()
        message.attachments.append(EmailAttachment(filename="attachment.docx", content=content_bytes))
        mail_processor.send_message(message=message)

    # Читаем последнее сообщение из папки inbox:
    inbox_messages = mail_processor.get_messages(count=1)
    last_message = inbox_messages[-1]
    print(last_message.subject)

    # Читаем сообщение от отправителя, например, мое письмо с другой почты
    inbox_messages_filtered = mail_processor.get_messages(folder="inbox", filter_func=lambda x: x.sender == "dreamsobenatic00@mail.ru", count=100)
    my_message = inbox_messages_filtered[-1]

    # Ответим на сообщение
    message = EmailMessage(
        subject = "Ответ на сообщение",
        body="Ну я понял короче, если что, то там, ну ты понял",
        recipients=[my_mail,],
        sender=my_mail,
    )
    mail_processor.send(message)

    mail_processor.quit()
