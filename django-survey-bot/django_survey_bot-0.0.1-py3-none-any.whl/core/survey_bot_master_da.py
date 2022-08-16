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

class SurveyBotMasterDA():
    
    def __init__(self):
        self.__exception = ExceptionHandler()
        self.__log = Logs()
    
    def create_chatbot(self, data):
        return Chatbot.objects.create(**data)

    def create_or_update_chatbot(self, data, bot_id=0):
        bot = Chatbot.objects
        if bot_id:
            bot = bot.filter(id=bot_id).update(**data)
        else:
            bot = bot.create(**data)
        return bot

    def create_or_update_chatbot_question(self, data, question_id=0):
        bot_question = ChatbotQuestions.objects
        if question_id:
            bot_question = bot_question.filter(id=question_id).update(**data)
        else:
            bot_question = bot_question.create(**data)
        return bot_question

    def delete_question_options_by_question_id(self, question_id):
        return ChatbotQuestionOptions.objects.filter(question_id=question_id).delete()

    def delete_question_options_by_question_ids(self, question_ids):
        return ChatbotQuestionOptions.objects.filter(question_id__in=question_ids).delete()

    def delete_question_by_question_id(self, question_id):
        return ChatbotQuestions.objects.filter(id=question_id).delete()

    def soft_delete_question_by_question_id(self, question_id):
        return ChatbotQuestionOptions.objects.filter(id=question_id).update(deleted=1)

    def bulk_create_question_options(self, data, question_id=0):
        data_list = []
        for each in data:
            data_list.append(
                ChatbotQuestionOptions(
                    question_id = question_id,
                    label = each['label'],
                    value=each['value']
                )
            )
        ChatbotQuestionOptions.objects.bulk_create(data_list)

    def create_question_options(self, data):
        return ChatbotQuestionOptions.objects.create(**data)

    def delete_chatbot_by_id(self, chatbot_id):
        return Chatbot.objects.filter(id=chatbot_id).update(deleted=1)

    def delete_questions_by_chatbot_id(self, chatbot_id):
        questions = ChatbotQuestions.objects.filter(chatbot_id=chatbot_id)
        question_ids = list(questions.values_list('id', flat=True))
        self.delete_question_options_by_question_ids(question_ids)
        questions.update(deleted=1)

    def create_chatbot_next_question_order(self, data):
        return ChatbotNextQuestionOrder.objects.create(**data)

    def delete_next_question_order_chatbot_id(self, chatbot_id):
        return ChatbotNextQuestionOrder.objects.filter(chatbot_id=chatbot_id).delete()

    def create_chatbot_data_collection_master(self, data):
        return ChatbotDataCollectionMaster.objects.create(**data)

    def update_chatbot_data_collection_master(self, data, master_id):
        return ChatbotDataCollectionMaster.objects.filter(id=master_id).update(**data)

    def create_chatbot_data_collection_details(self, data):
        return ChatbotDataCollectionDetails.objects.create(**data)

    def create_chatbot_jsplumb_connections(self, data):
        return ChatbotJsplumbConnections.objects.create(**data)

    def create_chatbot_jsplumb_positions(self, data):
        return ChatbotJsplumbFlowchartPositions.objects.create(**data)

    def delete_chatbot_jsplumb_positions_chatbot_id(self, chatbot_id):
        return ChatbotJsplumbFlowchartPositions.objects.filter(chatbot_id=chatbot_id).delete()

    def delete_chatbot_jsplumb_connections_chatbot_id(self, chatbot_id):
        return ChatbotJsplumbConnections.objects.filter(chatbot_id=chatbot_id).delete()