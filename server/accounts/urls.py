from django.urls import path
from .views import RegisterUserView

app_name= 'api'

urlpatterns = [
    path('', RegisterUserView.as_view(), name="register"),
]