from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from .serializers import UserRegisterSerializer
from rest_framework.response import Response
from rest_framework import status


class RegisterUserView(GenericAPIView):
    serializer_class = UserRegisterSerializer

    def Post(self, request):
        User_data=request.data
        serializer=self.serializer_class(data=User_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user=serializer.data
            #send email function user['email']
            return Response({
                'data':user,
                'message':f'hi {user.first_name} Thanks for signing up a passcode has been sent to your email'
            }, status=status.HTTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

