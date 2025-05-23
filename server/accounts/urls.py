from django.urls import path
from .views import *

app_name= 'auth'

urlpatterns = [
    path('register', RegisterUserView.as_view(), name="register"),
    path('varify-email/',VerifyUserEmail.as_view(), name='verify'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('profile/', TestAuthenticationView.as_view(), name='granted'),
    path('password-reset/', PasswordResetRequestView.as_view(), name="password-reset"),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirm.as_view(), name="password-reset-confirm"),
    path('set-new-password', SetNewPassword.as_view(), name="set-new-password"),
    path('logout/', LoginUserView.as_view(), name="logout"),
]