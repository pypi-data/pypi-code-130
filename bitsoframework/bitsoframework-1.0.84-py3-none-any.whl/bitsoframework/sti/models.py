import sys

from django.db import models
from django.db.models.base import ModelBase
from django.db.models.fields import Field

classes = {}
base_classes = []


class STIManager(models.Manager):
    def get_queryset(self):
        """
        only include objects in queryset matching current sti model type
        """
        queryset = super().get_queryset()
        if self.model not in base_classes:
            sti_type = self.model.get_sti_type(self.model)
            queryset = queryset.filter(sti_type=sti_type)
        return queryset


class STIModelBase(ModelBase):
    def __new__(cls, name, bases, attrs, **kwargs):

        if name != "STIModel":

            for base in bases:
                if base == STIModel:
                    model_class = super().__new__(cls, name, bases, attrs, **kwargs)
                    base_classes.append(model_class)
                    return model_class
                elif base in base_classes:
                    deleted = []
                    for key, value in attrs.items():
                        if isinstance(value, Field):
                            base.add_to_class(key, value)
                            deleted.append(key)

                    for key in deleted:
                        del attrs[key]

                    # define meta if not found
                    if not "Meta" in attrs:
                        class Meta(base.Meta):
                            pass

                        attrs["Meta"] = Meta

                    # by requirement, all sti classes must be proxy classes
                    attrs.get("Meta").proxy = True

                    model_class = super().__new__(cls, name, bases, attrs, **kwargs)

                    classes[model_class.get_sti_type(model_class)] = model_class

                    return model_class

        return super().__new__(cls, name, bases, attrs, **kwargs)


class STIModel(models.Model, metaclass=STIModelBase):
    class Meta:
        abstract = True

    objects = STIManager()
    sti_type = models.CharField(max_length=20)

    def save(self, *args, **kwargs):
        """
        automatically store the single-table-inheritance class name in the database
        """
        self.sti_type = self.get_sti_type(self.__class__)
        super().save(*args, **kwargs)

    def __new__(cls, *args, **kwargs):
        """
        create an instance corresponding to the single-table-inheritance type
        """
        model_class = cls
        try:
            field_name = "sti_type"
            sti_type = kwargs.get(field_name)
            if sti_type is None:
                sti_type_field_index = cls._meta.fields.index(
                    cls._meta.get_field(field_name))
                sti_type = args[sti_type_field_index]
            model_class = classes.get(sti_type) or model_class
        finally:
            return super().__new__(model_class)

    @staticmethod
    def get_sti_type(cls):
        return cls.__name__
