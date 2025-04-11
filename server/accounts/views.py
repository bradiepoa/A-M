from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from .serializers import UserRegisterSerializer,LoginSerializer
from rest_framework.response import Response
from rest_framework import status
from .utils import send_code_to_user
from .models import OneTimePassword


class RegisterUserView(GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request):
        User_data=request.data
        serializer=self.serializer_class(data=User_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user=serializer.data
            send_code_to_user(user['email'])
            #send email function user['email']
            return Response({
                'data':user,
                'message': f'Hi, thanks for signing up! A passcode has been sent to your email.'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class VerifyUserEmail(APIView):
    def post(self, request):
        otpcode = request.data.get('otp')
        try:
            user_code_obj = OneTimePassword.objects.get(code=otpcode)
            user = user_code_obj.user

            if not user.is_verified:
                user.is_verified = True
                user.save()
                user_code_obj.delete()

                return Response({
                    'message': 'Account email verified successfully'
                }, status=status.HTTP_200_OK)

            return Response({
                'message': 'User already verified'
            }, status=status.HTTP_200_OK)

        except OneTimePassword.DoesNotExist:
            return Response({
                'message': 'Invalid or expired verification code'
            }, status=status.HTTP_404_NOT_FOUND)

class LoginUserView(GenericAPIView):
    serializer_class=LoginSerializer
    def post(self, request):
        serializer=self.serializer_class(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        