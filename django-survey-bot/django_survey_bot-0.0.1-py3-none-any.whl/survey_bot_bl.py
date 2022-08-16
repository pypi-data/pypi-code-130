import json
import redis
from survey_bot.utils.exception_handler import ExceptionHandler
from survey_bot.utils.helper import UtilityHelper
from survey_bot.utils.logs import Logs
from django.shortcuts import render, redirect, reverse
from django.template import loader

from survey_bot.core.survey_bot_master_da import SurveyBotMasterDA
from survey_bot.core.survey_bot_replica_da import SureveyBotReplicaDA
from survey_bot.constants import BOT_QUESTION_FIELD_TYPE

class SurveyBotBL():
    def __init__(self):
        self.__exception = ExceptionHandler()
        self.__log = Logs()
        self.__helper = UtilityHelper()

    def manage_bot(self, request):
        response = None
        try:
            bot_obj = SureveyBotReplicaDA().get_all_bots()
            for bot in bot_obj:
                bot.chats = SureveyBotReplicaDA().get_chatbot_data_collection_master_by_bot_id(bot.id).count()
                bot.chats_finished = SureveyBotReplicaDA().get_chatbot_data_collection_master_by_bot_id(bot.id).filter(is_finished=1).count()
            context = {
                'bot':bot_obj,
            }
            response = render(request, 'index.html', context)
        except Exception as error:
            log_id = self.__log.error(
                f'Error in the method SurveyBotBL.manage_bot, Error: {str(error)},'
                f'Error traceback: {self.__exception.exception()}'
            )
        return response
    
    def save_chatbot_data(self, request):
        try:
            bot_dict = {}
            bot_dict['name'] = "New Bot"
            bot_obj = SurveyBotMasterDA().create_chatbot(bot_dict)
            if bot_obj:
                first_question = '''
                        <p>Hi, I'm Survey Bot.</p><p>I'm here to help you claim the compensation you deserve.</p>
                    '''
                unique_code = self.__helper.get_uuid()
                temp_dict = {}
                temp_dict['unique_code'] = unique_code
                temp_dict['chatbot_id'] = bot_obj.id
                temp_dict['question'] = first_question
                temp_dict['field_type'] = 1
                question = SurveyBotMasterDA().create_or_update_chatbot_question(temp_dict, 0)
                if question:
                    field_options = {}
                    field_options['question_id'] = question.id
                    field_options['label'] = "Let's get started"
                    field_options['value'] = "Let's get started"
                    SurveyBotMasterDA().create_question_options(field_options)
                return redirect('get_survey_bot',bot_id=bot_obj.id)
        except Exception as error:
            log_id = self.__log.error(
                f'Error in the method SurveyBotBL.save_chatbot_data, Error: {str(error)},'
                f'Error traceback: {self.__exception.exception()}'
            )

    def delete_bot(self, request):
        response = {'message':'', 'status':True, 'data':{}, 'is_created':False}
        try:
            chatbot_id = request.POST.get('bot_id',0)
            SurveyBotMasterDA().delete_chatbot_by_id(chatbot_id)
            SurveyBotMasterDA().delete_questions_by_chatbot_id(chatbot_id)
            SurveyBotMasterDA().delete_chatbot_jsplumb_connections_chatbot_id(chatbot_id)
            SurveyBotMasterDA().delete_chatbot_jsplumb_positions_chatbot_id(chatbot_id)
            SurveyBotMasterDA().delete_next_question_order_chatbot_id(chatbot_id)
            response['message'] = 'Bot has been deleted successfully'
        except Exception as error:
            log_id = self.__log.error(
                f'Error in the method SurveyBotBL.delete_chatbot, Error: {str(error)},'
                f'Error traceback: {self.__exception.exception()}'
            )
            response['message'] = 'Something went wrong.deletion failed'
            response['status'] = False
        return response
    
    def get_chatbot_data(self, request, bot_id):
        response = None
        try:
            jsplumb_connections_dict = {}
            bot_obj = SureveyBotReplicaDA().get_chatbot_by_id(bot_id)
            jsplumb_connections = SureveyBotReplicaDA().get_jsplumb_connections(bot_id)
            if jsplumb_connections:
                for conn in jsplumb_connections:
                    jsplumb_connections_dict[ conn.source] = conn.target
            context = {
                'bot':bot_obj,
                'question_type':BOT_QUESTION_FIELD_TYPE,
                'question_type_json':json.dumps(BOT_QUESTION_FIELD_TYPE),
                'jsplumb_connections':json.dumps(jsplumb_connections_dict),
            }
            response = render(request, 'create-bot.html', context)
        except Exception as error:
            log_id = self.__log.error(
                f'Error in the method SurveyBotBL.get_chatbot_data, Error: {str(error)},'
                f'Error traceback: {self.__exception.exception()}'
            )
        return response
    
    def ajax_get_chatbot_data(self, request):
        response = {'message':'', 'status':True, 'data':{}, 'is_created':False}
        try:
            bot_id = request.POST.get('bot_id')
            bot_obj = SureveyBotReplicaDA().get_chatbot_by_id(bot_id)
            if bot_obj:
                bot_obj = bot_obj.__dict__
                del bot_obj['_state']
                response['data'] = {
                    'bot':bot_obj,
                }
        except Exception as error:
            log_id = self.__log.error(
                f'Error in the method SurveyBotBL.ajax_get_chatbot_data, Error: {str(error)},'
                f'Error traceback: {self.__exception.exception()}'
            )
            response['status'] = False
            response['message'] = f"Error: {str(error)}"
        return response
    
    def ajax_save_chatbot_question(self, request):
        '''This will used to save question details'''
        response = {'message':'', 'status':True, 'data':{}, 'is_created':False}
        try:
            question_non_option_fields = []
            params_data = json.loads(request.POST.get('questionData', '{}'))
            question = params_data.get('question','')
            field_type = int(params_data.get('field_type',1))
            field_options = params_data.get('options',[])
            action = params_data.get('action','add')
            chatbot_id = params_data.get('chatbot_id')


            for key, value in BOT_QUESTION_FIELD_TYPE.items():
                if value['is_option'] == 0:
                    question_non_option_fields.append(key)

            temp_dict = {}
            temp_dict['chatbot_id'] = chatbot_id
            temp_dict['question'] = question
            temp_dict['field_type'] = field_type

            unique_code = self.__helper.get_uuid()
            question_id = params_data.get('question_id',0)
            if question_id:#will be edit
                question_obj = SureveyBotReplicaDA().get_chatbot_question_by_id(question_id)
                if question_obj:
                    unique_code = question_obj.unique_code
            try:
                if field_type == 4:
                    unique_code = f"name_{unique_code}"
                elif field_type == 5:
                    unique_code = f"email_{unique_code}"
                elif field_type == 7:
                    unique_code = f"phone_{unique_code}"
            except Exception as err:
                self.__log.error(
                    f'Error in the method SurveyBotBL().ajax_save_question, Error: {str(err)},'
                    f'Error traceback: {self.__exception.exception()}'
                )
            temp_dict['unique_code'] = unique_code
            question = SurveyBotMasterDA().create_or_update_chatbot_question(temp_dict, question_id)
            try:
                question_id = question.id
            except:
                pass
            temp_dict['question_id'] = question_id
            if question:
                SurveyBotMasterDA().delete_question_options_by_question_id(question_id)
                if field_type not in question_non_option_fields:
                    SurveyBotMasterDA().bulk_create_question_options(field_options, question_id)

            response['data'] = temp_dict
            response['is_created'] = True
            if action=='save':
                response['message'] = 'Changes Saved successfully'
            else:
                response['message'] = 'Your question created successfully'
        except Exception as error:
            log_id = self.__log.error(
                f'Error in the method SurveyBotBL).ajax_save_questionnaire_data, Error: {str(error)},'
                f'Error traceback: {self.__exception.exception()}'
            )
            response['status'] = False
            response['message'] = f'Error occured while processing data Error Code {log_id}'
        return response
    
    def get_all_chatbot_questions(self, request):
        response = {'message':'', 'status':True, 'data':{}}
        try:
            bot_id = int(request.POST.get('bot_id'))
            if bot_id:
                survey_bot_questions = SureveyBotReplicaDA().get_questions_by_chatbot_id(bot_id)
                if survey_bot_questions:
                    # create dataset for question order
                    bot_question_field_types = BOT_QUESTION_FIELD_TYPE
                    questons_data_list = []
                    for question in survey_bot_questions:
                        questions = {}
                        options_list = []
                        questions["question_id"] = question.id
                        questions["question"] = UtilityHelper().remove_html_tags(question.question)
                        questions["question_type"] = question.field_type
                        questions["is_option"] = bot_question_field_types[str(question.field_type)]['is_option']
                        questions["icon"] = bot_question_field_types[str(question.field_type)]['icon']
                        questions["label"] = bot_question_field_types[str(question.field_type)]['label']
                        question_options = SureveyBotReplicaDA().get_question_options_by_question_id(question.id)
                        if question_options:
                            for option in question_options:
                                options_dict = {}
                                options_dict['option_id'] = option.id
                                options_dict['option'] = option.label
                                options_list.append(options_dict)
                        questions['options'] = options_list
                        questons_data_list.append(questions)
                    next_question_order = SureveyBotReplicaDA().get_next_questions_by_chatbot_id(bot_id)
                    bot_questions = list(survey_bot_questions.values('id','question'))

                    template_context = {}
                    jsplumb_positions = SureveyBotReplicaDA().get_jsplumb_positions(bot_id)
                    if jsplumb_positions:
                        template_context['jsplumb_positions'] = jsplumb_positions

                    template_context['questons_data_list'] = questons_data_list
                    template_context['bot_questions'] = bot_questions
                    template_context['next_question_order'] = next_question_order
                    posts_html = loader.render_to_string('ajax-bot-question-order.html',template_context)
                    response = {'message':'', 'status':True, 'data':{"posts_html":posts_html}}
                else:
                    msg = 'No questions are created to publish the Chatbot'
                    response = {'message':msg, 'status':False, 'data':{}}
            else:
                response = {'message':'No Chatbot Id found', 'status':False, 'data':{}}       
        except Exception as error:
            log_id = self.__log.error(
                f'Error in the method SurveyBotBL.get_chatbot_questions, Error: {str(error)},'
                f'Error traceback: {self.__exception.exception()}'
            )
        return response
    
    def ajax_delete_question(self, request):
        '''This will used to delete question details'''
        response = {'message':'', 'status':True, 'data':{}, 'is_created':False}
        try:
            question_id = int(request.POST.get('question_id'))
            chatbot_id = int(request.POST.get('bot_id'))
            question_obj = SureveyBotReplicaDA().get_chatbot_question_by_id(question_id)
            if question_obj:
                SurveyBotMasterDA().delete_question_by_question_id(question_id)
                SurveyBotMasterDA().delete_question_options_by_question_id(question_id)
                response['message'] = "Question Deleted Successfully"
            else:
                response['status'] = False
                response['message'] = f'No Question is found with question id {question_id}'
        except Exception as error:
            log_id = self.__log.error(
                f'Error in the method SurveyBotBL().ajax_delete_question, Error: {str(error)},'
                f'Error traceback: {self.__exception.exception()}'
            )
            response['status'] = False
            response['message'] = f'Error occured while processing data Error Code {log_id}'
        return response
    
    def get_question_details(self,request):
        response = {'message':'', 'status':True, 'data':{}, 'is_created':False}
        options_list = []
        questions_data = {}
        try:
            chatbot_id = request.POST.get('bot_id')
            question_id = request.POST.get('question_id')
            if chatbot_id:
                questions_obj = SureveyBotReplicaDA().get_chatbot_question_by_id(question_id)
                if questions_obj:
                    question = questions_obj.question
                    question_type = questions_obj.field_type
                    if question_type == 1:
                        options_obj = SureveyBotReplicaDA().get_question_options_by_question_id(question_id)
                        if options_obj:
                            for option in options_obj:
                                options_list.append(option.value)
                    questions_data['question'] = question
                    questions_data['options'] = options_list
            response['data'] = questions_data
        except Exception as error:
            log_id = self.__log.error(
                f'Error in the method SurveyBotBL().get_question_details, Error: {str(error)},'
                f'Error traceback: {self.__exception.exception()}'
            )
            response['status'] = False
            response['message'] = f'Error occured while processing data Error Code {log_id}'
        return response
    
    def generate_question_order_dict(self,data_dict):
        processed_question_order_dict = {}
        try:
            for key,value in data_dict.items():
                question_order_dict = {}
                for qes_dic in value:
                    for option_key,option_value in qes_dic.items():
                        question_order_dict[option_key] = option_value
                        processed_question_order_dict[key] = question_order_dict
        except Exception as error:
            log_id = self.__log.error(
                f'Error in the method ChatbotBL.generate_question_order_dict, Error: {str(error)},'
                f'Error traceback: {self.__exception.exception()}'
            )
        return processed_question_order_dict
    
    def ajax_publish_chatbot(self, request):
        response = {'message':'', 'status':True, 'data':{}}
        try:
            chatbot_id = int(request.POST.get('bot_id'))
            is_publish = request.POST.get('is_publish',0)
            bot_name = request.POST.get('bot_name','New Bot')
            question_order_dict = json.loads(request.POST.get('questionOrderData', '{}'))
            jsplumb_connections_dict = json.loads(request.POST.get('jsplumbConnectionData', '{}'))
            jsplumb_flowchart_positions_dict = json.loads(request.POST.get('jsplumbPositionsData', '{}'))
            if chatbot_id:
                if question_order_dict:
                    question_order_dict = self.generate_question_order_dict(question_order_dict)
                    SurveyBotMasterDA().delete_next_question_order_chatbot_id(chatbot_id)
                    for ques_id, value in question_order_dict.items():
                        for option_key,next_question in value.items():
                            next_question_order = {}
                            next_question_order['chatbot_id'] = chatbot_id
                            next_question_order['question_id'] = ques_id
                            next_question_order['option_key'] = option_key
                            next_question_order['next_question'] = next_question
                            SurveyBotMasterDA().create_chatbot_next_question_order(next_question_order)

                if jsplumb_connections_dict:
                    SurveyBotMasterDA().delete_chatbot_jsplumb_connections_chatbot_id(chatbot_id)
                    for key,value in jsplumb_connections_dict.items():
                        connection_dict = {}
                        connection_dict['chatbot_id'] = chatbot_id
                        connection_dict['source'] = key
                        connection_dict['target'] = value
                        SurveyBotMasterDA().create_chatbot_jsplumb_connections(connection_dict)

                if jsplumb_flowchart_positions_dict:
                    SurveyBotMasterDA().delete_chatbot_jsplumb_positions_chatbot_id(chatbot_id)
                    for key,value in jsplumb_flowchart_positions_dict.items():
                        position_dict = {}
                        position_dict['chatbot_id'] = chatbot_id
                        position_dict['question_box_id'] = key
                        position_dict['position'] = value
                        SurveyBotMasterDA().create_chatbot_jsplumb_positions(position_dict)
                chatbot_questions_json = self.generate_json_for_chatbot(chatbot_id)
                SurveyBotMasterDA().create_or_update_chatbot({'is_published':0,'name':bot_name,'bot_questions_json':chatbot_questions_json}, chatbot_id)
            else:
                response = {'message':'No Chatbot id found', 'status':False, 'data':{}}

            if is_publish:
                SurveyBotMasterDA().create_or_update_chatbot({'is_published':1}, chatbot_id)
                msg = "Your Chatbot published successfully"
                response = {'message':msg, 'status':True, 'data':{}}
            else:
                SurveyBotMasterDA().create_or_update_chatbot({'is_published':0}, chatbot_id)

        except Exception as error:
            log_id = self.__log.error(
                f'Error in the method SurveyBotBL.ajax_publish_chatbot, Error: {str(error)},'
                f'Error traceback: {self.__exception.exception()}'
            )
            response['status'] = False
            response['message'] = f'Error occured while processing data Error Code {log_id}'
        return response
    
    def generate_json_for_chatbot(self, chatbot_id):
        bot_questions_dict = {}
        question_ids = []
        try:
            question_non_option_fields = []
            bot_question_field_type = BOT_QUESTION_FIELD_TYPE
            for key, value in bot_question_field_type.items():
                if value['is_option'] == 0:
                    question_non_option_fields.append(key)

            next_questions = SureveyBotReplicaDA().get_next_questions_by_chatbot_id(chatbot_id)
            if next_questions:
                for item in next_questions:
                    if not item.question_id in question_ids:
                        question_ids.append(item.question_id)
                    if not item.next_question in question_ids:
                        question_ids.append(item.next_question)
                questions = SureveyBotReplicaDA().get_questions_by_chatbot_id(chatbot_id)
                questions = questions.filter(id__in=question_ids)
                if questions:
                    for question in questions:
                        question_id = question.id
                        try:
                            chat_question = UtilityHelper().remove_empty_html_tags(question.question)
                        except:
                            chat_question = question.question
                        bot_questions_dict[question_id] = {}
                        bot_questions_dict[question_id]['question_code'] = question.unique_code
                        bot_questions_dict[question_id]['question'] = [chat_question]
                        bot_questions_dict[question_id]['answers'] = {}
                        if not question.field_type in question_non_option_fields:
                            options = SureveyBotReplicaDA().get_question_options_by_question_id(question_id)
                            answers = {}
                            for option in options:
                                answers[option.id] = option.label
                                bot_questions_dict[question_id]['answers'] = answers
                        bot_questions_dict[question_id]['expected_answer'] = {}
                        bot_questions_dict[question_id]['eligibility'] = {}
                        bot_questions_dict[question_id]['field_type'] = bot_question_field_type[str(question.field_type)]['type']
                        bot_questions_dict[question_id]['next_question'] = {}
                        next_question_order = SureveyBotReplicaDA().get_next_questions_by_question_id(question_id)
                        if next_question_order:
                            next_question = {}
                            for next in next_question_order:
                                next_question[next.option_key] = next.next_question
                                bot_questions_dict[question_id]['next_question'] = next_question
                        else:
                            bot_questions_dict[question_id]['next_question'] = {"default":"0"}

        except Exception as error:
            log_id = self.__log.error(
                f'Error in the method SurveyBotBL().generate_json_for_chatbot, Error: {str(error)},'
                f'Error traceback: {self.__exception.exception()}'
            )
        return json.dumps(bot_questions_dict)
    
    def surveybot_data_collection(self, request):
        redis_db = redis.StrictRedis(host='localhost', port='6379', db=0)
        response = {'status':True}
        try:
            output_html = ""
            next_question_id = 0
            # the get method is used to show the preview of the bot
            if request.method == 'GET':
                data = request.GET
            else:
                data = request.data

            chatbot_id = int(data.get('botId'))
            received_answer = str(data.get('answer'))
            question_id = str(data.get('question_id'))
            user_token = str(data.get('user_token'))
            questions_asked_key = f"questions_asked_{user_token}"
            is_collect_data = int(data.get('collect',0))
            data_collection = json.loads(data.get('data_collection',{}))
            try:
                questions = json.loads(redis_db.get(user_token))
            except:
                questions = []

            if not questions:
                json_questions = SureveyBotReplicaDA().get_chatbot_by_id(chatbot_id)
                if json_questions:
                    json_questions = json_questions.bot_questions_json
                    redis_db.set(user_token, json.dumps(json.loads(json_questions)))
                    questions = json.loads(redis_db.get(user_token))

            if questions:
                if question_id in ('restart','0'):
                    redis_db.delete(questions_asked_key)
                    questions_asked = json.dumps([])
                    redis_db.set(questions_asked_key, questions_asked)

                if not question_id in ('0','restart'):
                    for key,value in questions.items():
                        if question_id == key:
                            if 'answers' in value:
                                if received_answer in value['next_question']:
                                    next_question_id = value['next_question'][received_answer]
                                    break
                                else:
                                    next_question_id = value['next_question']['default']
                                    break

                # collect data in production mode
                if is_collect_data:
                    if data_collection:
                        self.store_chatbot_data_collection(request,chatbot_id,question_id,next_question_id,user_token,questions,data_collection)

                try:
                    questions_asked = json.loads(redis_db.get(questions_asked_key))
                except:
                    questions_asked = []

                if not questions_asked:
                    for key,value in questions.items():
                        if not key in questions_asked:
                            str_question_html = ""
                            question_code = value['question_code']
                            if 'question' in value:
                                for question in value['question']:
                                    additional_question = ""
                                    if value['field_type'] == 'text':
                                        additional_question = f'''<input type="text" class="phq-chat-input">
                                        <button data-question-code="{question_code}" data-question="{key}" data-answer="" data-label="" class="send icon is-right">[[send-button]]</button>'''
                                    elif value['field_type'] == 'email':
                                        additional_question = f'''<input type="email" class="phq-chat-input">
                                        <button data-question-code="{question_code}" data-question="{key}" data-answer="" data-label="" class="send icon is-right">[[send-button]]</button>'''
                                    elif value['field_type'] == 'phone':
                                        additional_question = f'''<input type="phone" class="phq-chat-input">
                                        <button data-question-code="{question_code}" data-question="{key}" data-answer="" data-label="" class="send icon is-right">[[send-button]]</button>'''
                                    elif value['field_type'] == 'date':
                                        additional_question = f'''<input type="date" class="phq-chat-input">
                                        <button data-question-code="{question_code}" data-question="{key}" data-answer="" data-label="" class="send icon is-right">[[send-button]]</button>'''
                                    elif value['field_type'] == 'number':
                                        additional_question = f'''<input type="number" class="phq-chat-input">
                                        <button data-question-code="{question_code}" data-question="{key}" data-answer="" data-label="" class="send icon is-right">[[send-button]]</button>'''
                                    elif value['field_type'] == 'textarea':
                                        additional_question = f'''<textarea class="phq-chat-input"></textarea>
                                        <button data-question-code="{question_code}" data-question="{key}" data-answer="" data-label="" class="send icon is-right">[[send-button]]</button>'''
                                    str_question_html += f'''
                                        <div class="phq-chat-msg phq-chat-left-msg">
                                            <div class="phq-chat-msg-bubble">
                                                <div class="phq-chat-msg-text">
                                                    {question}<div class="additional-inputs">
                                                    <div class="control  has-icons-right">
                                                    {additional_question}
                                                    </div>
                                                    <span style="color:red;font-size:12px;" class="error-msg"></span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    '''
                            if 'answers' in value:
                                str_question_html += '''<div class="phq-chat-msg phq-chat-left-msg">'''
                                for answer_key,answer in value['answers'].items():
                                    str_question_html += f'''
                                            <button data-question-code="{question_code}" data-question="{key}" data-answer="{answer_key}" data-label="{answer}"  class="send phq-btn">{answer}</button>
                                    '''
                                str_question_html+='''</div>'''
                            output_html+=str_question_html
                            questions_asked = json.dumps([key])
                            redis_db.set(questions_asked_key, questions_asked)
                            break
                else:
                    if next_question_id:
                        for key,value in questions.items():
                            if not key in questions_asked:
                                if int(key) != next_question_id:
                                    continue
                                question_code = value['question_code']
                                str_question_html = ""
                                if 'question' in value:
                                    for question in value['question']:
                                        additional_question = ""
                                        if value['field_type'] == 'text':
                                            additional_question = f'''<input type="text" class="phq-chat-input">
                                            <button data-question-code="{question_code}" data-question="{key}" data-answer="" data-label="" class="send icon is-right">[[send-button]]</button>'''
                                        elif value['field_type'] == 'email':
                                            additional_question = f'''<input type="email" class="phq-chat-input">
                                            <button data-question-code="{question_code}" data-question="{key}" data-answer="" data-label="" class="send icon is-right">[[send-button]]</button>'''
                                        elif value['field_type'] == 'phone':
                                            additional_question = f'''<input type="phone" class="phq-chat-input">
                                            <button data-question-code="{question_code}" data-question="{key}" data-answer="" data-label="" class="send icon is-right">[[send-button]]</button>'''
                                        elif value['field_type'] == 'date':
                                            additional_question = f'''<input type="date" class="phq-chat-input">
                                            <button data-question-code="{question_code}" data-question="{key}" data-answer="" data-label="" class="send icon is-right">[[send-button]]</button>'''
                                        elif value['field_type'] == 'number':
                                            additional_question = f'''<input type="number" class="phq-chat-input">
                                            <button data-question-code="{question_code}" data-question="{key}" data-answer="" data-label="" class="send icon is-right">[[send-button]]</button>'''
                                        elif value['field_type'] == 'textarea':
                                            additional_question = f'''<textarea class="phq-chat-input"></textarea>
                                            <button data-question-code="{question_code}" data-question="{key}" data-answer="" data-label="" class="send icon is-right">[[send-button]]</button>'''
                                        str_question_html += f'''
                                            <div class="phq-chat-msg phq-chat-left-msg">
                                                <div class="phq-chat-msg-bubble">
                                                    <div class="phq-chat-msg-text">
                                                        {question}<div class="additional-inputs">
                                                        <div class="control  has-icons-right">
                                                        {additional_question}
                                                        </div>
                                                        <span style="color:red;font-size:12px;" class="error-msg"></span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        '''
                                if 'answers' in value:
                                    str_question_html += '''<div class="phq-chat-msg phq-chat-left-msg">'''
                                    for answer_key,answer in value['answers'].items():
                                        str_question_html += f'''
                                            <button data-question-code="{question_code}" data-question="{key}" data-answer="{answer_key}" data-label="{answer}" class="send phq-btn">{answer}</button>
                                        '''
                                    str_question_html+='''</div>'''
                                output_html+=str_question_html
                                if not key in questions_asked:
                                    questions_asked.append(key)
                                    questions_asked = json.dumps(questions_asked)
                                    redis_db.set(questions_asked_key, questions_asked)
                                break
                    else:
                        #delete data from redis data base if the user completed all the questions
                        redis_db.delete(user_token)
                        redis_db.delete(questions_asked_key)
            else:
                output_html = """
                                <div class="phq-chat-msg phq-chat-left-msg">
                                        <div class="phq-chat-msg-bubble">
                                            <div class="phq-chat-msg-text">
                                                 Unfortunately, The bot could not find any questions for you.
                                            </div>
                                        </div>
                                    </div>
                                """
            response['data'] = output_html
        except Exception as error:
            log_id = self.__log.error(
                f'Error in the method SurveyBotBL.chatbot_data_collection, Error: {str(error)},'
                f'Error traceback: {self.__exception.exception()}'
            )
            response['status'] = False
        return response

    def store_chatbot_data_collection(self,request,chatbot_id,question_id,next_question_id,user_token,questions,data_collection):
        try:
            # check if master data existed
            master_data = SureveyBotReplicaDA().get_chatbot_data_collection_master_by_user_token(user_token)
            if not master_data:
                data_master = {}
                data_master['user_token'] = user_token
                data_master['chatbot_id'] = chatbot_id
                master_data = SurveyBotMasterDA().create_chatbot_data_collection_master(data_master)

            for key,value in data_collection.items():
                try:
                    question = UtilityHelper().remove_html_tags(questions[question_id]['question'][0])
                except:
                    question = questions[question_id]['question'][0]
                data_details = {}
                data_details['user_token'] = user_token
                data_details['question_code'] = key
                data_details['question'] = question
                data_details['answer'] = value
                SurveyBotMasterDA().create_chatbot_data_collection_details(data_details)

            next_question = int(questions[str(next_question_id)]['next_question']['default'])
            if not next_question:
                SurveyBotMasterDA().update_chatbot_data_collection_master({"is_finished":1},master_data.id)
        except Exception as error:
            log_id = self.__log.error(
                f'Error in the method SurveyBotBL.store_chatbot_data_collection, Error: {str(error)},'
                f'Error traceback: {self.__exception.exception()}'
            )
            
            