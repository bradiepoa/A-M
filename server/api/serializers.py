from api.models import User  # Import your custom User model
from rest_framework import serializers  # type: ignore

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "password", "role"]  # Removed "username"
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password", None)  # Extract password
        user = User(**validated_data)  # Create user instance without saving
        if password:
            user.set_password(password)  # Hash password
        user.save()  # Save the user with hashed password
        return user
