from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from .serializers import GoogleSignInSerializer
from rest_framework.response import Response
from rest_framework import status

# View to handle Google sign-in via access token
class GoogleSignInView(GenericAPIView):
    # Use the custom serializer for Google sign-in
    serializer_class = GoogleSignInSerializer

    def post(self, request):
        # Deserialize and validate the incoming data (access_token)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # If valid, serializer returns the registered/logged-in user data
        data = serializer.validated_data  # This includes user info from register_social_user

        # Return the user data as response (customize as needed)
        return Response(data, status=status.HTTP_200_OK)
