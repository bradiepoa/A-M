from rest_framework import serializers
from .utils import Google, register_social_user
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed

class GoogleSignInSerializer(serializers.Serializer):
    # This serializer expects an access_token from the client (Google OAuth2)
    access_token = serializers.CharField(min_length=6)
    def validate_access_token(self, access_token):
        # Use the custom Google utility to validate the token and get user data
        google_user_data = Google.validate(access_token)

        # If validation fails or data is None, raise an error
        if not google_user_data:
            raise serializers.ValidationError("Invalid or expired token.")
        # Ensure all required fields are present in the response
        required_fields = ['sub', 'email', 'given_name', 'family_name', 'aud']
        if not all(field in google_user_data for field in required_fields):
            raise serializers.ValidationError("Missing required fields in Google response.")
        # Verify that the token is intended for this app (matches your client ID)
        if google_user_data['aud'] != settings.GOOGLE_CLIENT_ID:
            raise AuthenticationFailed("Could not verify user: audience mismatch.")
        # Extract user data from the response
        email = google_user_data['email']
        first_name = google_user_data['given_name']
        last_name = google_user_data['family_name']
        provider = "google"  # OAuth provider
        # Call your utility function to register the user (or log them in)
        return register_social_user(provider, email, first_name, last_name)
