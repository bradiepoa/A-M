from google.auth.transport import requests
from google.oauth2 import id_token
from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from accounts.models import User


class Google:
    @staticmethod
    def validate(access_token):
        try:
            # ✅ Fix: Correct function call
            id_info = id_token.verify_oauth2_token(
                access_token, requests.Request(), settings.GOOGLE_CLIENT_ID
            )
            if id_info['iss'] in ['accounts.google.com', 'https://accounts.google.com']:
                return id_info
            else:
                raise AuthenticationFailed("Invalid issuer.")
        except Exception as e:
            print(f"Google token validation failed: {e}")
            raise AuthenticationFailed("Token is invalid or expired")


def login_user(email, password):
    user = authenticate(email=email, password=password)
    if not user:
        raise AuthenticationFailed("Invalid credentials.")
    
    user_tokens = user.tokens()  # Ensure this exists in your User model
    return {
        'email': user.email,
        'full_name': user.get_full_name(),
        'access_token': str(user_tokens.get('access')),
        'refresh_token': str(user_tokens.get('refresh'))
    }


def register_social_user(provider, email, first_name, last_name):
    try:
        user = User.objects.get(email=email)
        if user.auth_provider == provider:
            return login_user(email=email, password=settings.SOCIAL_AUTH_PASSWORD)
        else:
            raise AuthenticationFailed(
                detail=f"Please continue your login using {user.auth_provider}"
            )
    except User.DoesNotExist:
        new_user = User.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=settings.SOCIAL_AUTH_PASSWORD
        )
        new_user.auth_provider = provider
        new_user.is_verified = True  # Optional: make sure this field exists
        new_user.save()
        return login_user(email=new_user.email, password=settings.SOCIAL_AUTH_PASSWORD)
