from core.tasks import send_sms_task, send_otp_task


def send_sms_async(msg, numbers_list, delay_until=None):
    send_sms_task.delay(msg, numbers_list, delay_until)

def send_otp_async(otp, number):
    send_otp_task.delay(otp, number)