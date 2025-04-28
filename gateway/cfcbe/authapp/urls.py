from django.urls import path
from .views import RegisterUserView, RequestOTPView, VerifyOTPView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path("request-otp/", RequestOTPView.as_view(), name="request-otp"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
]


