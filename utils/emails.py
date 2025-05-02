from core.tasks import send_email_task

def send_email_async(subject, message, recipient_list, from_email=None):
    send_email_task.delay(subject, message, recipient_list, from_email)

