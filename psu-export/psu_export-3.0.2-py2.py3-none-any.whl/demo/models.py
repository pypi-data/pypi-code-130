from django.db import models
from psu_base.classes.Log import Log

log = Log()


class DemoOne(models.Model):

    code = models.CharField(max_length=12, blank=False, null=False, help_text="Some sort of code")
    title = models.CharField(max_length=80, blank=False, null=False)
    content = models.TextField(max_length=4000, blank=True, null=True)
    priority = models.IntegerField(blank=False, null=False)
    active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    date_created = models.DateField(auto_now_add=True)


class DemoTwo(models.Model):
    parent = models.ForeignKey(DemoOne, models.CASCADE, blank=False, null=False, db_index=True)
    detail = models.CharField(max_length=30, blank=False, null=False)
