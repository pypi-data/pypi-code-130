from django.urls import path, include
from django.contrib.auth.decorators import login_required
from .views import *


app_name = "twilio_2fa"


urlpatterns = [
    path(
        "",
        login_required(Twilio2FAStartView.as_view()),
        name="index",
    ),
    path(
        "register",
        login_required(Twilio2FARegisterView.as_view()),
        name="register"
    ),
    path(
        "change",
        login_required(Twilio2FAChangeView.as_view()),
        name="change"
    ),
    path(
        "start",
        login_required(Twilio2FAStartView.as_view()),
        name="start"
    ),
    path(
        "verify",
        login_required(Twilio2FAVerifyView.as_view()),
        name="verify"
    ),
    path(
        "success",
        login_required(Twilio2FASuccessView.as_view()),
        name="success"
    ),
    path(
        "failed",
        login_required(Twilio2FAFailedView.as_view()),
        name="failed"
    )
]
