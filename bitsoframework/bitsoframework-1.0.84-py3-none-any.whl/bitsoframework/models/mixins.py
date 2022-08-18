from django.db import models
from django.utils.translation import gettext_lazy as _


class RelaxedTitleDescriptionModel(models.Model):
    """
    TitleDescriptionModel

    An abstract base class model that provides title and description fields.
    """

    title = models.CharField(_('title'), max_length=255, blank=True, null=True)
    description = models.TextField(_('description'), blank=True, null=True)

    class Meta:
        abstract = True
