from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='survey_bot_index'),
    path('save-bot', views.save_bot, name='create_survey_bot'),
    path('bot/<int:bot_id>/', views.get_bot, name='get_survey_bot'),
    path('get-chat-bot-data', views.ajax_get_chatbot_data, name='ajax_get_chatbot_data'),
    path('save-bot-question', views.save_bot_question, name='save_bot_question'),
    path('get-all-questions/', views.ajax_get_chatbot_questions, name='ajax_get_chatbot_questions'),
    path('publish-bot', views.ajax_publish_chatbot, name='ajax_publish_chatbot'),
    path('delete-bot-question', views.ajax_delete_question, name='ajax_delete_question'),
    path('get-question-details', views.get_question_details, name='get_question_details'),
    path('delete-bot', views.delete_bot, name='delete_bot'),
    path('bot/view-chats/<int:bot_id>/', views.get_bot_chats_list, name='get_bot_chats_list'),
    path('bot/get-chats/', views.ajax_get_chatbot_chats, name='ajax_get_chatbot_chats'),
    path('bot/download-chats-as-csv/', views.downlaod_chats_as_csv, name='downlaod_chats_as_csv'),
    path('bot/downlaod_leads_in_chat/', views.downlaod_leads_in_chat, name='downlaod_leads_in_chat'),
    # data collection and chatbot apis
    path('api/', include('survey_bot.api.urls')),
    path('bot/view-chats-v1/<int:bot_id>/', views.get_bot__chats_list_table, name='get_bot_chats_list_table'),
    path('bot/get-ajax-listing',views.get_ajax_list, name="get_ajax_listing"),
    path('bot/delete-user-token',views.delete_user_token,name="delete_user_token"),
    path('bot/export-user-chat/<str:user>',views.export_user_chat,name="export_user_chat"),
    path('bot/help/',views.get_chatbot_help, name='survey_bot__help'),
   
]