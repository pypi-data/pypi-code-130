from django.apps import AppConfig
import threading
import os


class Alert360Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'alert360'
    verbose_name = 'The ultimate observability solution'

    def ready(self):
        # WARNING: This way the Thread wouldn't run if
        # Statereloader is off
        if os.environ.get('RUN_MAIN') == 'true':
            from .models import StateWatcher
            threading.Thread(
                name="StateWatcherLoop",
                target=StateWatcher.start,
                daemon=True
            ).start()
