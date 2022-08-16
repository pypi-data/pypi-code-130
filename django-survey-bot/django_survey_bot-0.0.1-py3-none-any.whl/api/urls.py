from django.urls import path
from survey_bot.api.views import ChatbotDataCollection,ChatbotDataCollectionTest

urlpatterns = [
    path('bot/master/', ChatbotDataCollection.as_view(), name="get_chatbot_api"),
    path('bot/master/test/', ChatbotDataCollectionTest.as_view(), name="get_chatbot_api_preview"),
]