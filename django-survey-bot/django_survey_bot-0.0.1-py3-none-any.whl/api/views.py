from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from survey_bot.survey_bot_bl import SurveyBotBL

class ChatbotDataCollection(APIView):
    # permission_classes = [HasAPIKey]#Api Authentication
    def put(self, request, format=None):
        result = SurveyBotBL().surveybot_data_collection(request)
        return Response(result)

class ChatbotDataCollectionTest(APIView):
    # permission_classes = [HasAPIKey]#Api Authentication
    def get(self, request, format=None):
        result = SurveyBotBL().surveybot_data_collection(request)
        return Response(result)