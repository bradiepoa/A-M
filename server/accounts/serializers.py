from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import smart_str, smart_bytes, force_str
from django.urls import reverse
from .utils import send_normal_email
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

class UserRegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(max_length=68, min_length=6, write_only=True)
    password2=serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model=User
        fields=['email','first_name','last_name','password','password2']
    
    def validate(self, attrs):
        password=attrs.get('password', '')
        password2=attrs.get('password2', '')

        if not password or not password2:
            raise serializers.ValidationError("Both password fields are required.")
        
        if password != password2:
            raise serializers.ValidationError("The passwords do not match.")     
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            password=validated_data.get('password')  # Corrected here
        )
        return user

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=6)
    password = serializers.CharField(max_length=68, write_only=True)
    full_name = serializers.CharField(max_length=68, read_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'full_name', 'access_token', 'refresh_token']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Accessing the request from the context
        request = self.context.get('request')

        # Authenticate the user
        user = authenticate(request, email=email, password=password)

        if not user:
            raise AuthenticationFailed("Invalid credentials. Please try again.")
        
        if not user.is_verified:
            raise AuthenticationFailed("Email is not verified.")
        
        # Generate user tokens
        user_tokens = user.tokens()  # Assuming `tokens()` method generates the tokens

        return {
            'email': user.email,
            'full_name': user.get_full_name(),  # Call as a method
            'access_token': str(user_tokens.get('access')),
            'refresh_token': str(user_tokens.get('refresh'))
        }

class PasswordResetRequestSerializer(serializers.Serializer):
    email=serializers.EmailField(max_length=255)
    class Meta:
        fields=['email',]
    def validate(self, attrs):
        email=attrs.get('email')
        # check is user with email exist in our db
        if User.objects.filter(email=email).exists():
            user=User.objects.get(email=email)
            uidb64=urlsafe_base64_encode(smart_bytes(user.id))
            token=PasswordResetTokenGenerator().make_token(user)
            request=self.context.get('request')
            site_domain=get_current_site(request).domain
            relative_link=reverse('auth:password-reset-confirm', kwargs={'uidb64':uidb64, 'token':token})
            abslink=f"http://{site_domain}{relative_link}"
            email_body=f"Hey, use the email below to reset your password \n {abslink}"
            data={
                'email_body':email_body,
                'email_subject':"Reset your password",
                'to_email':user.email                
            }
            send_normal_email(data)

        return super().validate(attrs)

class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=100, min_length=6, write_only=True)
    confirm_password = serializers.CharField(max_length=100, min_length=6, write_only=True)
    uidb64= serializers.CharField(write_only=True)
    token= serializers.CharField(write_only=True)
    class Meta:
        fields=["password", "confirm_password","uidb64","token"]
    
    def validate(self, attrs):
        try:

            token=attrs.get('token')
            uidb64=attrs.get('uidb64')
            password=attrs.get('password')
            confirm_password=attrs.get('confirm_password')

            user_id=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed("Resent link is inavlid or has expired", 401)
            if password != confirm_password:
                raise AuthenticationFailed("Password do not match")
            user.set_password(password)
            user.save()
            return user
                
            return super().validate(attrs)
        except Exception as e:
            return AuthenticationFailed("link is invalid or expired")


class LogoutUserSerializer(serializers.Serializer):
    refresh_token=serializers.CharField()

    default_error_message={
        'bad_token':('token is Invalid or has expired')
    }
    
    def validate(self, attrs):
        self.token=attrs.get('refresh_token')
        return attrs

    def save(self, **kwargs):
        try:
            token=RefreshToken(self.token)
            token.blacklist()

        except TokenError:
            return self.fail('bad_token')