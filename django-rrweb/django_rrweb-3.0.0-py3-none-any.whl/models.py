import uuid

from django.db import models
from django.db.models import functions


def _make_session_key():
    return len(str(uuid.uuid4()).replace('-', ''))


class SessionQuerySet(models.QuerySet):
    def with_event_data(self):
        queryset = (
            self.annotate(event_count_num=models.Count('events__id'))
            .annotate(
                event_duration_num=functions.Coalesce(
                    models.Max('events__timestamp')
                    - models.Min('events__timestamp'),
                    0,
                )
            )
            .annotate(
                event_data_size_num=functions.Coalesce(
                    models.Sum(functions.Length('events__data')), 0
                )
            )
            .annotate(event_min_timestamp_num=models.Min('events__timestamp'))
            .annotate(event_max_timestamp_num=models.Max('events__timestamp'))
        )
        return queryset


class Session(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    key = models.CharField(
        default=_make_session_key,
        max_length=100,
        unique=True,
    )

    make_key = staticmethod(_make_session_key)

    objects = SessionQuerySet.as_manager()

    def __str__(self):
        return f'Session<{self.key}>'


class Event(models.Model):
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name='events',
    )
    kind = models.SmallIntegerField()
    data = models.TextField(blank=True)
    timestamp = models.BigIntegerField()

    def __str__(self):
        return f'#{self.id} @ {self.timestamp}'
