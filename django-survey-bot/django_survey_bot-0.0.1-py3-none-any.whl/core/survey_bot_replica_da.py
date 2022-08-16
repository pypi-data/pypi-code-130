from survey_bot.models import Chatbot
from survey_bot.models import ChatbotQuestions
from survey_bot.models import ChatbotQuestionOptions
from survey_bot.models import ChatbotNextQuestionOrder
from survey_bot.models import ChatbotDataCollectionMaster
from survey_bot.models import ChatbotDataCollectionDetails
from survey_bot.models import ChatbotJsplumbConnections
from survey_bot.models import ChatbotJsplumbFlowchartPositions


from survey_bot.utils.exception_handler import ExceptionHandler
from survey_bot.utils.logs import Logs

class SureveyBotReplicaDA():
    
    def __init__(self):
        self.__exception = ExceptionHandler()
        self.__log = Logs()

    def get_all_bots(self, user_ids=[]):
        return Chatbot.objects.filter(deleted=0).order_by('-id')
    
    def get_chatbot_question_by_id(self, question_id):
        return ChatbotQuestions.objects.filter(id=question_id).first()

    def get_question_options_by_question_id(self, question_id):
        return ChatbotQuestionOptions.objects.filter(question_id=question_id)

    def get_questions_by_chatbot_id(self, chatbot_id):
        return ChatbotQuestions.objects.filter(chatbot_id=chatbot_id, deleted=0)

    def get_chatbot_by_user_ids(self, user_ids=[]):
        return Chatbot.objects.filter(created_by__in=user_ids, deleted=0)

    def get_published_chatbot_by_user_ids(self, user_ids=[]):
        return Chatbot.objects.filter(created_by__in=user_ids,deleted=0, is_published=1)

    def get_chatbot_by_id(self, chatbot_id):
        return Chatbot.objects.filter(id=chatbot_id).first()

    def get_chatbot_question_by_unique_code(self, unique_code):
        return ChatbotQuestions.objects.filter(unique_code=unique_code, deleted=0).first()

    def get_next_questions_by_question_id(self, question_id):
        return ChatbotNextQuestionOrder.objects.filter(question_id=question_id)

    def get_next_questions_by_chatbot_id(self, chatbot_id):
        return ChatbotNextQuestionOrder.objects.filter(chatbot_id=chatbot_id)

    def get_chatbot_data_collection_master_by_user_token(self, user_token):
        return ChatbotDataCollectionMaster.objects.filter(user_token=user_token).first()

    def get_chatbot_data_collection_master_by_bot_id(self, chatbot_id):
        return ChatbotDataCollectionMaster.objects.filter(chatbot_id=chatbot_id, deleted=0).order_by('-id')

    def get_chatbot_data_collection_detail_by_user_token(self, user_token):
        return ChatbotDataCollectionDetails.objects.filter(user_token=user_token)

    def get_jsplumb_connections(self,chatbot_id):
        return ChatbotJsplumbConnections.objects.filter(chatbot_id=chatbot_id)

    def get_jsplumb_positions(self,chatbot_id):
        return ChatbotJsplumbFlowchartPositions.objects.filter(chatbot_id=chatbot_id)

    def get_all_chatbot_data_collection_master_by_bot_id_and_status(self, chatboat_id, is_finished):
        return  ChatbotDataCollectionMaster.objects.filter(chatbot_id=chatboat_id, is_finished__in = is_finished)

    def get_chat_details_by_user_tokens(self, user_tokens):
        return  ChatbotDataCollectionDetails.objects.filter(user_token__in = user_tokens)
    
    def get_chatbot_data_collection_detail_by_user_token_lst(self, user_token=[]):
        return ChatbotDataCollectionDetails.objects.filter(user_token__in=user_token)

    def get_all_chatbot_data_collection_master_by_bot_id(self, chatbot_id):
        return ChatbotDataCollectionMaster.objects.filter(chatbot_id=chatbot_id, deleted=0).order_by('-id')
    
    def delete_user_token_by_bot_id(self, token, id):
        return  ChatbotDataCollectionMaster.objects.filter(user_token=token, chatbot_id=id).update(deleted=1)
    


    
    
    


   
