from django.db import models
from psu_base.classes.Log import Log
from psu_base.services import auth_service, utility_service
from urllib.parse import urlencode
from django.urls import reverse

log = Log()


class ExportApp(models.Model):
    app_code = models.CharField(
        max_length=50,
        help_text="Application whose tables may be exported.",
        db_index=True,
        unique=True
    )

    export_app = models.CharField(
        max_length=50,
        help_text="Used in S3 export file path"
    )

    export_enabled = models.BooleanField(default=False)

    def models(self):
        return self.exportmodel_set.all()

    @classmethod
    def get(cls, pk):
        try:
            if str(pk).isnumeric():
                return cls.objects.get(pk=pk)
            else:
                return cls.objects.get(app_code=pk)
        except cls.DoesNotExist:
            return None


class ExportModel(models.Model):
    app = models.ForeignKey(ExportApp, models.CASCADE, db_index=True)
    name = models.CharField(max_length=30, db_index=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    export_enabled = models.BooleanField(default=False)

    def fields(self):
        return self.exportfield_set.all()

    def enabled_fields(self):
        return self.exportfield_set.filter(export_enabled=True)

    @classmethod
    def get(cls, pk):
        try:
            return cls.objects.get(pk=pk)
        except cls.DoesNotExist:
            return None

    @classmethod
    def find(cls, app, model_name):
        try:
            return cls.objects.get(app=app, name=model_name)
        except cls.DoesNotExist:
            return None


class ExportField(models.Model):
    model = models.ForeignKey(ExportModel, models.CASCADE, db_index=True)
    name = models.CharField(max_length=80, db_index=True)
    data_type = models.CharField(max_length=50)
    key = models.CharField(max_length=50, null=True, blank=True)
    suggested_cognos_name = models.CharField(max_length=30)
    suggested_cognos_stage_type = models.CharField(max_length=30)
    suggested_cognos_type = models.CharField(max_length=30)
    description = models.CharField(max_length=500, null=True, blank=True)
    format_data = models.CharField(max_length=50, null=True, blank=True)
    export_enabled = models.BooleanField(default=False)

    @classmethod
    def get(cls, pk):
        try:
            return cls.objects.get(pk=pk)
        except cls.DoesNotExist:
            return None

    @classmethod
    def find(cls, model, field_name):
        try:
            return cls.objects.get(model=model, name=field_name)
        except cls.DoesNotExist:
            return None
