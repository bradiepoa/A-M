from django.urls import path
from .views import *

app_name= 'auth'

urlpatterns = [
    path('register', RegisterUserView.as_view(), name="register"),
    path('varify-email/',VerifyUserEmail.as_view(), name='verify'),
    path('login/', LoginUserView.as_view(), name='login')
]