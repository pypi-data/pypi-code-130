from telecms.apps import AppConfig


class ServiceExchangeConfig(AppConfig):
    name = 'telecms_django'

    def ready(self):
        from telecms_bridge_base import configuration
        from telecms_django.configuration import ServiceExchangeConfiguration
        conf = ServiceExchangeConfiguration()
        configuration.set_configuration(conf)
        from telecms_bridge_base.commands.check_token import check_token_command
        check_token_command('/telecms_api/')
        from telecms_bridge_base.db import connect_database_from_settings
        connect_database_from_settings()
