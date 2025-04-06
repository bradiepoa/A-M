import random
from django.core.mail import EmailMessage

def generate_otp():
    otp = ""
    for i in range(6):
        otp += str(random.randint(1, 9))
    return otp
