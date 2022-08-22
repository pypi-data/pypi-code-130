#!/usr/bin/env python
# -*- coding: utf-8 -*-
class ParamMessage:
    MERCHANT_ID = "merchant_id"
    MESSAGE_TYPE = "message_type"
    SOURCE = "source"
    KEY_CONFIG = "key_config"
    ACCOUNT_IDS = "account_ids"
    EMAIL_MERCHANT_ID = "email_merchant_id"
    EMAIL_SENDER_TYPE = "email_sender_type"
    EMAIL_SENDER_ID = "email_sender_id"
    EMAIL_SENDER_DOMAIN = "email_sender_domain"
    EMAIL_SENDER_NAME = "email_sender_name"
    DATA_KWARGS = "data_kwargs"
    LIST_FIELD_REQUIRED = [MERCHANT_ID, KEY_CONFIG]


class MessageTypeValue:
    SEND_ALL = "send_all"
    SEND_SOCKET = "send_socket"
    SEND_EMAIL = "send_email"
    SEND_PUSH_ID_MOBILE_APP = "send_push_id_mobile_app"

