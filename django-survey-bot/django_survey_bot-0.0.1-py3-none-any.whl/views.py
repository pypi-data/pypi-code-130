import json
from multiprocessing import context
from urllib import response
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from survey_bot.survey_bot_bl import SurveyBotBL
from survey_bot.survey_bot_chats_bl import SurveyBotChatsBL

def index(request):
    response = SurveyBotBL().manage_bot(request)
    return response if response else render(request, 'error-404.html')

def save_bot(request):
    return SurveyBotBL().save_chatbot_data(request)
    
def get_bot(request,bot_id):
    response = SurveyBotBL().get_chatbot_data(request,bot_id)
    return response if response else render(request, 'error-404.html')

def ajax_get_chatbot_questions(request):
    return JsonResponse(SurveyBotBL().get_all_chatbot_questions(request))

def save_bot_question(request):
    return JsonResponse(SurveyBotBL().ajax_save_chatbot_question(request))

def ajax_publish_chatbot(request):
    return JsonResponse(SurveyBotBL().ajax_publish_chatbot(request))

def ajax_delete_question(request):
    return JsonResponse(SurveyBotBL().ajax_delete_question(request))

def get_question_details(request):
    return JsonResponse(SurveyBotBL().get_question_details(request))

def delete_bot(request):
    return JsonResponse(SurveyBotBL().delete_bot(request))

def ajax_get_chatbot_data(request):
    return JsonResponse(SurveyBotBL().ajax_get_chatbot_data(request))

def get_bot_chats_list(request,bot_id):
    response = SurveyBotChatsBL().get_bot_chats_list(request,bot_id)
    return response if response else render(request, 'error-404.html')

def ajax_get_chatbot_chats(request):
    return JsonResponse(SurveyBotChatsBL().ajax_get_chatbot_chats(request))

def downlaod_chats_as_csv(request):
    data = SurveyBotChatsBL().downlaod_chats_as_csv(request)
    return data

def downlaod_leads_in_chat(request):
    data = SurveyBotChatsBL().downlaod_leads_in_chat(request)
    return data

def get_bot__chats_list_table(request, bot_id):
    response = SurveyBotChatsBL().get_bot_chats_list_table(request, bot_id)
    return response if response else render(request, 'error-404.html')

def get_ajax_list(request):
    response = SurveyBotChatsBL().get_ajax_list(request)
    return JsonResponse(response)

def delete_user_token(request):
    response = SurveyBotChatsBL().delete_user_token(request)
    return JsonResponse(response)

def export_user_chat(request,user):
    response = SurveyBotChatsBL().export_user_chat(request,user)
    return response

def get_chatbot_help(request):
    response = SurveyBotChatsBL().get_chatbot_help(request)
    return response
    


