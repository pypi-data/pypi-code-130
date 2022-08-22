#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time

from confluent_kafka import Producer
from mobio.libs.Singleton import Singleton

from .config import MobioEnvironment, ConsumerTopic
from .constant import ParamMessage, MessageTypeValue


@Singleton
class MobioNotifySDK(object):
    PREFIX_LOGGER = "[NOTIFY_SDK]"
    PREFIX_LOGGER_ERR = "[NOTIFY_SDK_ERR]"

    def __init__(self):
        self.source = ""
        self.email_merchant_id = ""
        self.email_sender_id = ""
        self.email_sender_domain = ""
        self.email_sender_name = ""

    def config(self, source):
        self.source = source
        return self

    def config_send_email(self, merchant_id, sender_id, sender_domain, sender_name=None):
        """
        :param merchant_id: ID cấu hình gửi email của từng thương hiệu được cấu hình trên Module Notify Manager
        :param  sender_id: Email người gửi (không bắt buộc) (Ex: noreply@mobio.vn)
        :param sender_domain: Domain được cấu hình để gửi email đến (Ex: mobio.vn)
        :param sender_name: Tên người gửi/tên nguồn gửi (Ex: Mobio Alert)
        Lưu ý: Mỗi merchant sẽ có từng cấu hình khác nhau theo từng yêu cầu gửi về kênh email nào,
        vui lòng liên hệ module Notify Manager(NM) để được hỗ trợ.
        """
        self.email_merchant_id = merchant_id
        self.email_sender_id = sender_id
        self.email_sender_domain = sender_domain
        self.email_sender_name = sender_name
        return self

    def validate_data_send_notify(self, message_type, **kwargs):
        """
        Kiểm tra các trường thông tin message thông báo và dữ liệu khởi tạo
        :param kwargs:
        :param message_type:
        :return:
        """
        if not self.source:
            raise Exception("{} {} is require".format(MobioNotifySDK.PREFIX_LOGGER_ERR, "source"))

        if message_type == MessageTypeValue.SEND_ALL or message_type == MessageTypeValue.SEND_EMAIL:
            if not self.email_merchant_id:
                raise Exception("{} {} config send email is require".format(MobioNotifySDK.PREFIX_LOGGER_ERR,
                                                                            "merchant_id"))

            # if not self.email_sender_domain:
            #     raise Exception("{} {} is require".format(MobioNotifySDK.PREFIX_LOGGER_ERR, "email_sender_domain"))

        print("{}: validate_data_send_notify: kwargs: {}".format(MobioNotifySDK.PREFIX_LOGGER, kwargs))
        list_field_validate = ParamMessage.LIST_FIELD_REQUIRED
        for field in list_field_validate:
            if not kwargs.get(field):
                raise Exception("{} {} is require".format(MobioNotifySDK.PREFIX_LOGGER_ERR, field))

        if kwargs.get(ParamMessage.ACCOUNT_IDS) and isinstance(kwargs.get(ParamMessage.ACCOUNT_IDS), list) is False:
            raise Exception("{} account_ids is list".format(MobioNotifySDK.PREFIX_LOGGER_ERR))

    @staticmethod
    def get_data_kwargs(data_kwargs: dict):
        result = dict()
        if data_kwargs:
            for key, val in data_kwargs.items():
                result[key] = val

        return result

    def build_message_send_notify(self, message_type, merchant_id,
                                  key_config, account_ids, kwargs):
        message = {
            ParamMessage.MESSAGE_TYPE: message_type,
            ParamMessage.SOURCE: self.source,
            ParamMessage.MERCHANT_ID: merchant_id,
            ParamMessage.KEY_CONFIG: key_config,
            ParamMessage.ACCOUNT_IDS: account_ids
        }
        if message_type == MessageTypeValue.SEND_EMAIL or message_type == MessageTypeValue.SEND_ALL:
            message.update({
                ParamMessage.EMAIL_MERCHANT_ID: self.email_merchant_id,
                ParamMessage.EMAIL_SENDER_ID: self.email_sender_id,
                ParamMessage.EMAIL_SENDER_DOMAIN: self.email_sender_domain,
                ParamMessage.EMAIL_SENDER_NAME: self.email_sender_name,
            })
        message.update({
            ParamMessage.DATA_KWARGS: MobioNotifySDK.get_data_kwargs(kwargs)
        })

        return message

    def send_message_notify(self, merchant_id, key_config, account_ids, **kwargs):
        """
        Thực hiện việc gửi thông báo toàn kênh (Mobile App, Browser, Web(in-app), Email)
        Bắt buộc: Yêu cầu khởi tạo cấu hình email nếu muốn dùng hàm xử lý này!

        :param merchant_id: ID thương hiệu cần gửi thông báo
        :param key_config: kiểu thông báo (được cấu hình trên admin) (ex: 'jb_create_by_me_end',
        'jb_estimate_target_size')
        :param account_ids: danh sách id nhân viên (id nhân viên của module ADMIN)
        :param kwargs: Thông tin các field nội dung thông báo toàn kênh định dạng key=value
        Truyền định dạng send_message_notify_sdk(merchant_id, key_config, account_ids, deal_count=5) lên hàm xử lý.
        SDK sẽ tự bắt thông tin field để thực hiện replace theo nội dung đã được cấu hình trên Admin.
        EX: title: Thông báo đơn hàng tồn quá **deal_count** đơn.
            content: Thông báo đơn hàng tồn quá **deal_count** đơn.
                    Vui lòng phân công cho nhân viên xử lý.
        - Field chuẩn hoá gửi kênh email truyền thêm các field sau(vì là kwargs vui lòng truyền đúng định dạng key=value):
            + email_file_alert: boolean (File thông báo ko có button giá trị = False, có button giá trị = True,
             mặc định giá trị = False)
            + email_button_name: string (Tên button email, mặc định ko truyền lên filed này sẽ có giá trị = "Tải file",
                                        email_file_alert = False bỏ qua field này)
            + email_url_file: string (đường dẫn khi submit vào button email; email_file_alert = False bỏ qua field này)
            + email_subject: string (nếu muốn tự custom tiêu đề email)
            + email_content: string html (nếu muốn tự custom nội dung email) (chỉ là nội dung bên trong,
             không chưa cả khung template)
        - Field chuẩn hoá gửi kênh socket (gửi theo kênh push_id cũng lấy thông tin theo fields này)
         truyền thêm các field sau (vì là kwargs vui lòng truyền đúng định dạng key=value):
            + socket_title: string (Nếu muốn tự custom tiêu đề gửi đến các kênh App, Browser, Web)
            + socket_content: string (Nếu muốn tự custom nội dung gửi đến các kênh App, Browser, Web)
        """
        start_time = time.time()

        message_type = MessageTypeValue.SEND_ALL
        MobioNotifySDK().validate_data_send_notify(message_type, merchant_id=merchant_id, key_config=key_config,
                                                   account_ids=account_ids)

        data_send_producer = self.build_message_send_notify(message_type, merchant_id,
                                                            key_config, account_ids, kwargs)

        MobioNotifySDK.push_message_to_topic_receive(json.dumps(data_send_producer))
        print("{}: send_message_notify_sdk: time_process:: {}".format(
            MobioNotifySDK.PREFIX_LOGGER, time.time() - start_time))

    def send_message_notify_socket(self, merchant_id, key_config, account_ids, **kwargs):
        """
        Thực hiện việc gửi thông báo socket đến các kênh Mobile App, Browser, Web In App

        :param merchant_id: ID thương hiệu cần gửi thông báo
        :param key_config: kiểu thông báo (được cấu hình trên admin) (ex: 'jb_create_by_me_end',
        'jb_estimate_target_size')
        :param account_ids: danh sách id nhân viên (id nhân viên của module ADMIN)
        :param kwargs: Thông tin các field nội dung thông báo toàn kênh định dạng key=value
        Truyền định dạng send_message_notify_sdk(merchant_id, key_config, account_ids, deal_count=5) lên hàm xử lý.
        SDK sẽ tự bắt thông tin field để thực hiện replace theo nội dung đã được cấu hình trên Admin.
        EX: title: Thông báo đơn hàng tồn quá **deal_count** đơn.
            content: Thông báo đơn hàng tồn quá **deal_count** đơn.
                    Vui lòng phân công cho nhân viên xử lý.

        - Field chuẩn hoá gửi kênh socket truyền thêm các field sau (vì là kwargs vui lòng truyền đúng định dạng key=value):
            + title: string (Nếu muốn tự custom tiêu đề gửi đến các kênh App, Browser, Web)
            + content: string (Nếu muốn tự custom nội dung gửi đến các kênh App, Browser, Web)
        """
        start_time = time.time()

        message_type = MessageTypeValue.SEND_SOCKET
        MobioNotifySDK().validate_data_send_notify(message_type, merchant_id=merchant_id, key_config=key_config,
                                                   account_ids=account_ids)

        data_send_producer = self.build_message_send_notify(message_type, merchant_id,
                                                            key_config, account_ids, kwargs)

        MobioNotifySDK.push_message_to_topic_receive(json.dumps(data_send_producer))
        print("{}: send_message_notify_socket: time_process:: {}".format(
            MobioNotifySDK.PREFIX_LOGGER, time.time() - start_time))

    def send_message_notify_email(self, merchant_id, key_config, account_ids, **kwargs):
        """
        Hàm thực hiện việc gửi email thông báo
        Bắt buộc: Yêu cầu khởi tạo cấu hình email nếu muốn dùng hàm xử lý này

        :param merchant_id: ID thương hiệu cần gửi thông báo
        :param key_config: kiểu thông báo (được cấu hình trên admin) (ex: 'jb_create_by_me_end',
        'jb_estimate_target_size')
        :param account_ids: danh sách id nhân viên (id nhân viên của module ADMIN)
        :param kwargs: Thông tin các field nội dung thông báo toàn kênh định dạng key=value
        Truyền định dạng send_message_notify_sdk(merchant_id, key_config, account_ids, deal_count=5) lên hàm xử lý.
        SDK sẽ tự bắt thông tin field để thực hiện replace theo nội dung đã được cấu hình trên Admin.
        EX: title: Thông báo đơn hàng tồn quá **deal_count** đơn.
            content: Thông báo đơn hàng tồn quá **deal_count** đơn.
                    Vui lòng phân công cho nhân viên xử lý.
        - Field chuẩn hoá gửi kênh email truyền thêm các field sau(vì là kwargs vui lòng truyền đúng định dạng key=value):
            + file_alert: boolean (File thông báo ko có button giá trị = False, có button giá trị = True,
             mặc định giá trị = False)
            + button_name: string (Tên button email, mặc định ko truyền lên filed này sẽ có giá trị = "Tải file",
                                        email_file_alert = False bỏ qua field này)
            + url_file: string (đường dẫn khi submit vào button email; email_file_alert = False bỏ qua field này)
            + subject: string (nếu muốn tự custom tiêu đề email)
            + content: string html (nếu muốn tự custom nội dung email) (chỉ là nội dung bên trong,
             không chưa cả khung template)
        """
        start_time = time.time()

        message_type = MessageTypeValue.SEND_EMAIL
        MobioNotifySDK().validate_data_send_notify(message_type, merchant_id=merchant_id, key_config=key_config,
                                                   account_ids=account_ids)

        data_send_producer = self.build_message_send_notify(message_type, merchant_id, key_config,
                                                            account_ids, kwargs)
        MobioNotifySDK.push_message_to_topic_receive(json.dumps(data_send_producer))
        print("{}: send_message_notify_email: time_process:: {}".format(
            MobioNotifySDK.PREFIX_LOGGER, time.time() - start_time))

    def send_message_notify_push_id_mobile_app(self, merchant_id, key_config, account_ids, **kwargs):
        """
        Hàm thực hiện việc gửi thông báo qua đầu push_id (Firebase Notification)
        :param merchant_id: ID thương hiệu cần gửi thông báo
        :param key_config: kiểu thông báo (được cấu hình trên admin) (ex: 'jb_create_by_me_end',
        'jb_estimate_target_size')
        :param account_ids: danh sách id nhân viên (id nhân viên của module ADMIN)
        :param kwargs: Thông tin các field nội dung thông báo toàn kênh định dạng key=value
        Truyền định dạng send_message_notify_sdk(merchant_id, key_config, account_ids, deal_count=5) lên hàm xử lý.
        SDK sẽ tự bắt thông tin field để thực hiện replace theo nội dung đã được cấu hình trên Admin.
        EX: title: Thông báo đơn hàng tồn quá **deal_count** đơn.
            content: Thông báo đơn hàng tồn quá **deal_count** đơn.
                    Vui lòng phân công cho nhân viên xử lý.

        - Field chuẩn hoá gửi kênh push_id mobile app truyền thêm các field sau (vì là kwargs vui lòng truyền đúng định dạng key=value):
            + title: string (Nếu muốn tự custom tiêu đề gửi)
            + content: string (Nếu muốn tự custom nội dung gửi)
        """
        start_time = time.time()

        message_type = MessageTypeValue.SEND_PUSH_ID_MOBILE_APP
        MobioNotifySDK().validate_data_send_notify(message_type, merchant_id=merchant_id, key_config=key_config,
                                                   account_ids=account_ids)

        data_send_producer = self.build_message_send_notify(message_type, merchant_id, key_config,
                                                            account_ids, kwargs)
        MobioNotifySDK.push_message_to_topic_receive(json.dumps(data_send_producer))
        print("{}: send_message_notify_push_id_mobile_app: time_process:: {}".format(
            MobioNotifySDK.PREFIX_LOGGER, time.time() - start_time))

    @staticmethod
    def push_message_to_topic_receive(data):
        """
        Bắn message đến topic SDK nhận tin xử lý
        :param data:
        :return:
        """
        conf = {
            "request.timeout.ms": 20000,
            "bootstrap.servers": MobioEnvironment.KAFKA_BROKER,
            "compression.type": "zstd"
        }

        producer = Producer(conf)

        topic_sdk = ConsumerTopic.TOPIC_NOTIFY_SDK_RECEIVE_MESSAGE
        producer.produce(topic_sdk, data)
        producer.poll(0)
        print("{}: push_message_to_topic: topic: {}".format(MobioNotifySDK.PREFIX_LOGGER, topic_sdk))
        print("{}: push_message_to_topic: message: {}".format(MobioNotifySDK.PREFIX_LOGGER, data))
        producer.flush()
