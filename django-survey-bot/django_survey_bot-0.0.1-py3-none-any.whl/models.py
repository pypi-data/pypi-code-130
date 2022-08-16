from django.db import models

class Chatbot(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=1000, blank=True, null=True)
    created_by = models.IntegerField(default=0)
    is_published = models.SmallIntegerField(blank=True, null=True)
    bot_questions_json = models.JSONField(blank=True, null=True)
    brand_name = models.CharField(max_length=200, blank=True, null=True)
    brand_sub_title = models.CharField(max_length=200, blank=True, null=True)
    chatbot_position  = models.CharField(max_length=200, default="right")
    chatbot_primary_color = models.CharField(max_length=200, default="#34436A")
    button_background_color = models.CharField(max_length=200, default="#34436A")
    button_text_color = models.CharField(max_length=200, default="#ffffff")
    auto_show = models.CharField(max_length=200, default="true")
    created_at = models.DateTimeField(auto_now=True)
    deleted = models.SmallIntegerField(default=0)

class ChatbotQuestionOptions(models.Model):
    question_id = models.IntegerField()
    label = models.CharField(max_length=500, blank=True, null=True)
    value = models.CharField(max_length=500, blank=True, null=True)

class ChatbotQuestions(models.Model):
    unique_code = models.CharField(unique=True, max_length=100)
    chatbot_id = models.IntegerField()
    question = models.CharField(max_length=500)
    description = models.CharField(max_length=1000, blank=True, null=True)
    field_type = models.IntegerField()
    expected_answer = models.CharField(max_length=1000, blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    deleted = models.SmallIntegerField(default=0)

class ChatbotNextQuestionOrder(models.Model):
    chatbot_id = models.IntegerField()
    question_id = models.IntegerField()
    option_key = models.CharField(max_length=100)
    next_question = models.IntegerField()

class ChatbotDataCollectionMaster(models.Model):
    source = models.CharField(max_length=100)
    user_token = models.CharField(max_length=150)
    chatbot_id = models.IntegerField(default=0)
    is_finished = models.IntegerField(default=0)
    submited_at = models.DateTimeField(auto_now=True)
    deleted = models.IntegerField(default=0)

class ChatbotDataCollectionDetails(models.Model):
    user_token = models.CharField(max_length=150)
    question_code = models.CharField(max_length=255)
    question = models.CharField(max_length=5000)
    answer = models.CharField(max_length=1000)

class ChatbotJsplumbFlowchartPositions(models.Model):
    chatbot_id = models.IntegerField()
    question_box_id = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=150)

class ChatbotJsplumbConnections(models.Model):
    chatbot_id = models.IntegerField()
    source = models.CharField(max_length=100, blank=True, null=True)
    target = models.CharField(max_length=100, blank=True, null=True)