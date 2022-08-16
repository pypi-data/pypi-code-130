from django.contrib.postgres.fields import ArrayField as DjangoArrayField
from django.forms import TypedMultipleChoiceField

from .forms import SelectArrayField


__all__ = ['ArrayField']


class ArrayField(DjangoArrayField):
    def formfield(self, **kwargs):
        defaults = {}
        if self.base_field.choices:
            defaults = {
                'form_class': SelectArrayField,
                'base_field': self.base_field.formfield(choices_form_class=TypedMultipleChoiceField)
            }
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)
