import logging
logger = logging.getLogger('analytics')
try:
    from core.celery import app
    from celery import shared_task
    from django_celery_beat.models import PeriodicTask, IntervalSchedule

    @app.on_after_finalize.connect
    def setup_period_tasks(sender, **kwargs):
        schedule, created = IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.HOURS)
        task, created = PeriodicTask.objects.get_or_create(name="Update Analytics Dataset",
                                                        task='analytics.tasks.update_dataset_from_dashboards',
                                                        defaults={'interval': schedule,
                                                                    'expire_seconds': 60 * 15})

    @shared_task(bind=True)
    def update_dataset_from_dashboards(self, *args, **kwargs):
        """
        Triggers for expiring the chat sessions on lumiahook
        Every bot can have this functionality enabled, with a default closing message.
        """
        pass
except Exception as exc:    
    logger.error(f"Erro Celery setup for Analytics app: {exc}",)    
    pass