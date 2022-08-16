import json
import redis
import datetime
from django.db.models import Q
from survey_bot.utils.exception_handler import ExceptionHandler
from survey_bot.utils.helper import UtilityHelper
from survey_bot.utils.logs import Logs
from django.shortcuts import render, redirect, reverse
from django.template import loader
from django.http import HttpResponse

from survey_bot.core.survey_bot_master_da import SurveyBotMasterDA
from survey_bot.core.survey_bot_replica_da import SureveyBotReplicaDA
from survey_bot.constants import BOT_QUESTION_FIELD_TYPE

import csv

class SurveyBotChatsBL():
    def __init__(self):
        self.__exception = ExceptionHandler()
        self.__log = Logs()
        self.__helper = UtilityHelper()
    
    def get_bot_chats_list(self,request,bot_id):
        response = None
        try:
            bot_obj = SureveyBotReplicaDA().get_chatbot_by_id(bot_id)
            chats_master_obj = SureveyBotReplicaDA().get_chatbot_data_collection_master_by_bot_id(bot_id)
            context = {
                'bot':bot_obj,
                'chats_master':chats_master_obj
            }
            response = render(request, 'list-chats.html', context)
        except Exception as error:
            log_id = self.__log.error(
                f'Error in the method SurveyBotChatsBL.get_bot_chats_list, Error: {str(error)},'
                f'Error traceback: {self.__exception.exception()}'
            )
        return response
    
    def ajax_get_chatbot_chats(self, request):
        response = {'message':'', 'status':True, 'data':{}, 'is_created':False}
        try:
            token = request.POST.get('token')
            chats = SureveyBotReplicaDA().get_chatbot_data_collection_detail_by_user_token(token)
            if chats:
                template_context = {
                    'chats':chats
                }
                posts_html = loader.render_to_string('ajax-chats.html',template_context)
                response['data']['posts_html'] = posts_html
        except Exception as error:
            log_id = self.__log.error(
                f'Error in the method SurveyBotChatsBL.ajax_get_chatbot_chats, Error: {str(error)},'
                f'Error traceback: {self.__exception.exception()}'
            )
            response['status'] = False
            response['message'] = f"Error: {str(error)}"
        return response

    def downlaod_chats_as_csv(self, request):
        user_tokens = []
        response = None
        try:
            status = request.POST.get('status')
            chatbot_id = request.POST.get('bot-id')
            if status:
                is_finished_in = [status]
            else:
                is_finished_in = [0, 1]
            chat_bot = SureveyBotReplicaDA().get_chatbot_by_id(chatbot_id)
            finished_chatbot_data = SureveyBotReplicaDA(
            ).get_all_chatbot_data_collection_master_by_bot_id_and_status(chatbot_id, is_finished_in)
            for each_finished_chat in finished_chatbot_data:
                user_tokens.append(each_finished_chat.user_token)
            if user_tokens:
                qstn_answers = SureveyBotReplicaDA().get_chat_details_by_user_tokens(user_tokens)
            file_name = chat_bot.name + ' responses.csv'
            response = HttpResponse(
                content_type='text/csv',
                headers={'Content-Disposition': 'attachment; filename='+file_name},)
            writer = csv.writer(response)
            field_names = ['Token', 'Question', 'Anwser']
            writer.writerow(field_names)
            for each_qstn_answer in qstn_answers:
                qstn = ''
                answr = ''
                user_token = ''
                qstn = each_qstn_answer.question
                answr = each_qstn_answer.answer
                user_token = each_qstn_answer.user_token
                writer.writerow([ user_token, qstn, answr])
        except Exception as error:
            self.__log.error(
                f'Error in the method SurveyBotChatsBL.downlaod_chats_as_csv, Error: {str(error)},'
                f'Error traceback: {self.__exception.exception()}'
            )
        return response

    def downlaod_leads_in_chat(self, request):
        user_tokens = []
        response = None
        qstn_dict = {}
        try:
            chatbot_id = request.POST.get('chatbotid')
            is_finished_in = [0, 1]
            chat_bot = SureveyBotReplicaDA().get_chatbot_by_id(chatbot_id)
            finished_chatbot_data = SureveyBotReplicaDA(
            ).get_all_chatbot_data_collection_master_by_bot_id_and_status(chatbot_id, is_finished_in)
            for each_finished_chat in finished_chatbot_data:
                user_tokens.append(each_finished_chat.user_token)
            if user_tokens:
                qstn_answers = SureveyBotReplicaDA().get_chat_details_by_user_tokens(user_tokens)
            file_name = chat_bot.name + ' leads.csv'
            response = HttpResponse(
                content_type='text/csv',
                headers={'Content-Disposition': 'attachment; filename='+file_name},)
            writer = csv.writer(response)
            field_names = ['Name', 'Email', 'Phone']
            writer.writerow(field_names)
            for each_qstn_answer in qstn_answers:
                qstn = ''
                answr = ''
                user_token = each_qstn_answer.user_token
                if user_token not in qstn_dict:
                    qstn_dict[user_token] = {}
                if "name" in each_qstn_answer.question_code :
                    qstn_dict[user_token]['name'] = each_qstn_answer.answer
                if "phone" in each_qstn_answer.question_code :
                    qstn_dict[user_token]['phone'] = each_qstn_answer.answer
                if "email" in each_qstn_answer.question_code :
                    qstn_dict[user_token]['email'] = each_qstn_answer.answer
            for each_response in qstn_dict:
                if 'phone' in qstn_dict[each_response] or 'email' in  qstn_dict[each_response]:
                        name = qstn_dict[each_response].get("name", None)
                        phone = qstn_dict[each_response].get("phone", None)
                        email = qstn_dict[each_response].get("email", None)
                        writer.writerow([ name, email, phone])
        except Exception as error:
            self.__log.error(
                f'Error in the method SurveyBotChatsBL.downlaod_leads_in_chat, Error: {str(error)},'
                f'Error traceback: {self.__exception.exception()}'
            )
        return response
    
    def get_bot_chats_list_table(self, request, bot_id):
        response = None
        master_lst = []
        try:
            
            bot_obj = SureveyBotReplicaDA().get_chatbot_by_id(bot_id)
            chats_master_obj = SureveyBotReplicaDA().get_chatbot_data_collection_master_by_bot_id(bot_id)
            for i in chats_master_obj:
                master_lst.append(i.user_token)
            context = {
                    'bot':bot_obj,
                    'chats_master':chats_master_obj,
                }   
           
            chats = SureveyBotReplicaDA().get_chatbot_data_collection_detail_by_user_token_lst(master_lst)
            if chats : 
                context['chats'] = chats
            
            response = render(request, 'table-list-chat.html', context)
        except Exception as error:
            log_id = self.__log.error(
                f'Error in the method SurveyBotChatsBL.get_bot_chats_list_table, Error: {str(error)},'
                f'Error traceback: {self.__exception.exception()}'
            )
        return response

    def get_ajax_list(self, request):
        list_data = []
        userTokenLst = []
        response={'recordsTotal': 0,'recordsFiltered': 0,'data': []}
        result_total = 0
        result_filtered = 0
        try:
           
            draw = int(request.POST.get('draw', 0))

           
            start = int(request.POST.get('start', 0))

           
            length = int(request.POST.get('length', 0))


            month = request.POST.get('month',0)
            yearonly = request.POST.get('yearonly',0)
            search = request.POST.get('search',"")
            id = request.POST.get('id', 0)
            result = SureveyBotReplicaDA().get_all_chatbot_data_collection_master_by_bot_id(id)
            if not month and not yearonly and not search:
                result = result[:10]
            result_total = result.count()
            if month:
                result = result.filter(submited_at__month=month)
                result_count = result.count()
            if yearonly:
                result = result.filter(submited_at__year=yearonly)
                result_count = result.count()
            for eachItem in result:
                userTokenLst.append(eachItem.user_token)
            if search:
                result2 = SureveyBotReplicaDA().get_chatbot_data_collection_detail_by_user_token_lst(userTokenLst)
                result2 = result2.filter(answer__icontains=search)
                test = []
                if not result2:
                    return response
                for eachRow in result2:
                    if not eachRow.user_token in test:
                        test.append(eachRow.user_token)
                if test:
                    result = result.filter(user_token__in=test)
                result_count = result.count()
            if month or yearonly or search:
                result_filtered = result_count
            else:
                result_filtered = result_total
            result = result[start: (start + length)]

            for eachItem in result:
                data = []
                data.append(eachItem.submited_at.strftime("%B %d, %Y %H:%I %p"))
                data.append(eachItem.user_token)
                button = f"""<a href='#'  class='view'  title='View Chat' data-user-token-id='{eachItem.user_token}'>
                <i class='fas fa-comments'></i></a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href='javascript:void(0)' 
                class='delete' title='Delete User Chat' data-delete-token-id='{eachItem.user_token}'>
                <i class='fa-solid fa-trash-can'></i></a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                <a href='/survey-bot/bot/export-user-chat/{eachItem.user_token}' class='export' title='Export Chat'  data-export-token-id='{eachItem.user_token}'>
                <i class='fa-solid fa-file-export'></i></a>"""
                data.append(button)
                list_data.append(data) 
            response['data'] = list_data
            response['recordsTotal'] = result_total
            response['recordsFiltered'] = result_filtered
        except Exception as error:
            log_id = self.__log.error(
                f'Error in the method SurveyBotChatsBL.get_ajax_list, Error: {str(error)},'
                f'Error traceback: {self.__exception.exception()}'
            )
        return response

    def delete_user_token(self, request):
        response = {'error' : True, 'success' : False}
        try:
            token = request.POST.get('token', 0)
            id = request.POST.get('id', 0)
            result = SureveyBotReplicaDA().delete_user_token_by_bot_id(token, id)
            if result:
                response['success'] = True
        except Exception as error:
            log_id = self.__log.error(
                f'Error in the method SurveyBotChatsBL.delete_user_token, Error: {str(error)},'
                f'Error traceback: {self.__exception.exception()}'
            )
        return response

    def export_user_chat(self, request,user):
        response = {'error' : '','success' : ''}
        chat_lst = []
        try:
            token = user
            chat = SureveyBotReplicaDA().get_chatbot_data_collection_detail_by_user_token(token)
            file_name = token + ' leads.csv'
            response = HttpResponse(
                content_type='text/csv',
                headers={'Content-Disposition': 'attachment; filename='+file_name},)
            writer = csv.writer(response)
            field_names = ['User','Question','Answer']
            writer.writerow(field_names)
            for each_qstn_answer in chat:
                qstn = ''
                answer = ''
                user_token = ''
                qstn = each_qstn_answer.question
                answer = each_qstn_answer.answer
                user_token = each_qstn_answer.user_token
                writer.writerow([ user_token, qstn, answer])
        except Exception as error:
            log_id = self.__log.error(
                f'Error in the method SurveyBotChatsBL.export_user_chat, Error: {str(error)},'
                f'Error traceback: {self.__exception.exception()}'
            )
        return response

    def get_chatbot_help(self, request):
        response = None
        try:
            response = render(request, 'help-chatbot.html', context = {})
        except Exception as error:
            log_id = self.__log.error(
                f'Error in the method SurveyBotChatsBL.get_chatbot_help, Error: {str(error)},'
                f'Error traceback: {self.__exception.exception()}'
            )
        return response



        


        
            
            


            
        


            

        
           

        
                                        

        
        

        


        

        

    
        