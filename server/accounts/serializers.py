from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate
from rest_framework.exception import AuthenticationFailed

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
    email=serializers.EmailFiled(max_length=255, min_length=6)
    password=serializers.CharField(max_length=68, write_only=True)
    full_name = serializers.CharField(max_length=68, read_only=True)
    access_token=serializers.CharField(max_length=255, read_only=True)
    refresh_token=serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model=User
        fields=['email', 'password','full_name','access_token','refresh_token']
    
    def validate(self, attrs):
        email=attrs.get('email')
        password=attrs.get('password')
        request.self.context.get('request')
        user=authenticate(request, email=email, password=password)
        # vailid user by checking the db
        if not user:
            raise AuthenticationFailed("Invalid credentials try again")
        if not user.is_varified:
            raise AuthenticationFailed("Email is not varified")
        # try to generate token if user exist
        user_tokens=user.tokens()

        return {
            'emal':user.email,
            'full_name':user.get_full_name,
            'access_token':str(user_tokens.get('access')),
            'refresh_token':str(user_tokens.get('refresh'))
        }