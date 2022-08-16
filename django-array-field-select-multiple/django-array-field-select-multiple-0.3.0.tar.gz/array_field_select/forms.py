from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.forms import Field


__all__ = ['SelectArrayField']


class SelectArrayField(Field):
    def __init__(self, base_field, max_length, **kwargs):
        self.base_field = base_field
        self.base_field.choices = self.base_field.choices[1:]
        self.max_length = max_length
        self.widget = self.base_field.widget
        super(SelectArrayField, self).__init__(**kwargs)

    def clean(self, value):
        value = self.base_field.clean(value)
        value = super(SelectArrayField, self).clean(value)
        return self.base_field.clean(value)

    def validate(self, value):
        if value and self.max_length and len(value) > self.max_length:
            raise ValidationError(_('You can only choose {} or fewer options.  You chose {}'.format(self.max_length, len(value))))
