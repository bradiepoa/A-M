from google.auth.transport import requests
from google.oauth2 import id_token
from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed


class Google():
    @staticmethod
    def validate(access_token):
        try:
            id_info=id_token.varify_oauth2_token(access_token(access_token, requests.Request))
            if "accounts.google.com" in id_info['iss']:
                return id_info

        except Exception as e:
            return "token is invalide or expired"