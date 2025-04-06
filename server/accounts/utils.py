import random
from django.core.mail import EmailMessage
from django.conf import settings
from .models import User,OneTimePassword

def generate_otp():
    otp = ""
    for i in range(6):
        otp += str(random.randint(1, 9))
    return otp

def send_code_to_user(email):
    subject = "One-time passcode for Email verification"
    otp_code = generate_otp()
    print("Generated OTP:", otp_code)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return "User with this email does not exist."

    current_site = "myAth.com"
    email_body = (
        f"Hi\n\n"
        f"Thanks for signing up on {current_site}!\n"
        f"Please verify your email with this one-time passcode: {otp_code}\n\n"
        f"If you did not request this, please ignore this email."
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    # Save or update the OTP in the database
    OneTimePassword.objects.update_or_create(user=user, defaults={'code': otp_code})
    # Send the email
    d_email = EmailMessage(subject=subject, body=email_body, from_email=from_email, to=[email])
    d_email.send(fail_silently=True)

    return "OTP sent successfully!"

