from django.core.mail import send_mail
from django.conf import settings


def send_otp_via_email(email, otp):
    print('email sent')
    subject = "Email Verification"
    message = f'Your OTP For FindMyChild is {otp}'
    email_from = settings.EMAIL_HOST
    send_mail(subject, message, email_from, [email])
