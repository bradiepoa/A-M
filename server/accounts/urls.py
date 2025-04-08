from django.urls import path
from .views import *

app_name= 'api'

urlpatterns = [
    path('', RegisterUserView.as_view(), name="register"),
    path('varify-email/',VerifyUserEmail.as_view(), name='verify'),
]