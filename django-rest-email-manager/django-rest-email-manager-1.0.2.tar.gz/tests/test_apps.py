from django.apps import apps

from rest_email_manager.apps import RestEmailManagerConfig


def test_apps():
    assert RestEmailManagerConfig.name == "rest_email_manager"
    assert (
        apps.get_app_config("rest_email_manager").name == "rest_email_manager"
    )
