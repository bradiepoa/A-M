from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _

class User(AbstractBaseUser, PermissionsMixin):
    email=models.EmailField(max_length=255, unique=True, verbose_name=_("Email Address"))
    first_name=models.CharField(max_length=200, verbose_name=_("First Name"))
    last_name=models.CharField(max_length=200, verbose_name=_("Last Name"))
    is_staff=models.BooleanField(default=False)
    is_superviser=models.BooleanField(default=False)
    is_verified=models.BooleanField(default=False)
    is_active=models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    USER_NAME_FIELDS="email"
    REQUIRED_FIELDS= ["first_name", "last_name"]

    objects= UserManager()

    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name}  {self.last_name}"

