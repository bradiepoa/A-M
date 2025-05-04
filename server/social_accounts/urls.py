from django.urls import path
from .views import GoogleSignInView

app_name="social_accounts"
urlpatterns=[
    path('google/', GoogleSignInView.as_views(), name='google'),
]