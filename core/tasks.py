import json

import requests
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from core.settings import DEFAULT_FROM_EMAIL
from utils.loggers import log_info, log_error


@shared_task(bind=True, max_retries=3)
def send_email_task(self, subject, message, recipient_list, from_email=None):
    try:
        from_email = from_email or DEFAULT_FROM_EMAIL
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False,
        )
        log_info(f"Email sent to {recipient_list}")
    except Exception as e:
        log_error(f"Failed to send email: {e}")
        raise self.retry(exc=e, countdown=60)


# delay_until format: "yyyyMMddHHmm"
@shared_task(bind=True, max_retries=3)
def send_sms_task(self,msg, numbers_list, delay_until=None):
    numbers_list = ','.join(numbers_list).replace('+', '')

    log_info(f"Sending SMS to {numbers_list}")

    url = f"https://smsmisr.com/api/SMS/?environment={settings.SMSMISR_ENVIRONMENT}&username={settings.SMSMISR_USERNAME}&password={settings.SMSMISR_PASSWORD}&language={settings.SMSMISR_LANGUAGE}&sender={settings.SMSMISR_SENDER_TOKEN}&mobile={numbers_list}&message={msg}"
    if delay_until:
        url += f"&DelayUntil={delay_until}"

    response = requests.post(url)
    response = response.json()

    print("code: ", response.get('code'))
    print("success code: ", settings.SMSMISR_SUCCESS_SMS_CODE)

    if response.get('code') == settings.SMSMISR_SUCCESS_SMS_CODE:
        log_info(f"SMS sent successfully to {numbers_list}")
    else:
        log_error(f"Failed to send SMS: {response}")


@shared_task(bind=True, max_retries=3)
def send_otp_task(self,otp, number):

    number = number.replace('+', '')
    log_info(f"Sending OTP to {number}")

    url = f"https://smsmisr.com/api/OTP/?environment={settings.SMSMISR_ENVIRONMENT}&username={settings.SMSMISR_USERNAME}&password={settings.SMSMISR_PASSWORD}&sender={settings.SMSMISR_SENDER_TOKEN}&mobile={number}&template={settings.SMSMISR_OTP_TEMPLATE_TOKEN}&otp={otp}"
    response = requests.post(url)
    response = response.json()

    print("code: ", response.get('Code'))
    print("success code: ", settings.SMSMISR_SUCCESS_OTP_CODE)

    if response.get('Code') == settings.SMSMISR_SUCCESS_OTP_CODE:
        log_info(f"OPT sent successfully to {number}")
    else:
        log_error(f"Failed to send OTP: {response}")
