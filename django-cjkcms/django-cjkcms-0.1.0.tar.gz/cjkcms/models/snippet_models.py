"""
Snippets are for content that is re-usable in nature.
"""

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.core.models import (
    Orderable,
)  # problems with unique slug! <- TranslatableMixin
from wagtail.snippets.models import register_snippet
from wagtail.images import get_image_model_string

from cjkcms.blocks import (
    HTML_STREAMBLOCKS,
    LAYOUT_STREAMBLOCKS,
    NAVIGATION_STREAMBLOCKS,
)
from cjkcms.settings import cms_settings
from cjkcms.fields import CjkcmsStreamField


@register_snippet
class Carousel(ClusterableModel):
    """
    Model that represents a Carousel. Can be modified through the snippets UI.
    Selected through Page StreamField bodies by the CarouselSnippetChooser in
    snippet_choosers.py
    """

    class Meta:
        verbose_name = _("Carousel")

    name = models.CharField(
        max_length=255,
        verbose_name=_("Name"),
    )
    show_controls = models.BooleanField(
        default=True,
        verbose_name=_("Show controls"),
        help_text=_(
            "Shows arrows on the left and right of the carousel to advance next or previous slides."
        ),  # noqa
    )
    show_indicators = models.BooleanField(
        default=True,
        verbose_name=_("Show indicators"),
        help_text=_(
            "Shows small indicators at the bottom of the carousel based on the number of slides."
        ),  # noqa
    )
    animation = models.CharField(
        blank=True,
        max_length=20,
        choices=None,
        default="",
        verbose_name=_("Animation"),
        help_text=_("The animation when transitioning between slides."),
    )

    panels = [
        MultiFieldPanel(
            heading=_("Slider"),
            children=[
                FieldPanel("name"),
                FieldPanel("show_controls"),
                FieldPanel("show_indicators"),
                FieldPanel("animation"),
            ],
        ),
        InlinePanel("carousel_slides", label=_("Slides")),
    ]

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        """
        Inject custom choices and defaults into the form fields
        to enable customization of settings without causing migration issues.
        """
        super().__init__(*args, **kwargs)
        # Set choices dynamically.
        self._meta.get_field(
            "animation"
        ).choices = cms_settings.CJKCMS_FRONTEND_CAROUSEL_FX_CHOICES  # type: ignore
        # Set default dynamically.
        if not self.id:  # type: ignore
            self.animation = cms_settings.CJKCMS_FRONTEND_CAROUSEL_FX_DEFAULT


class CarouselSlide(Orderable, models.Model):
    """
    Represents a slide for the Carousel model. Can be modified through the
    snippets UI.
    """

    class Meta:
        verbose_name = _("Carousel Slide")

    carousel = ParentalKey(
        Carousel,
        related_name="carousel_slides",
        verbose_name=_("Carousel"),
    )
    image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Image"),
    )
    background_color = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Background color"),
        help_text=_("Hexadecimal, rgba, or CSS color notation (e.g. #ff0011)"),
    )
    custom_css_class = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Custom CSS class"),
    )
    custom_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Custom ID"),
    )
    content = CjkcmsStreamField(HTML_STREAMBLOCKS, blank=True, use_json_field=True)

    panels = [
        FieldPanel("image"),
        FieldPanel("background_color"),
        FieldPanel("custom_css_class"),
        FieldPanel("custom_id"),
        FieldPanel("content"),
    ]


@register_snippet
class Classifier(ClusterableModel):
    """
    Simple and generic model to organize/categorize/group pages.
    """

    class Meta:
        verbose_name = _("Classifier")
        verbose_name_plural = _("Classifiers")
        ordering = ["name"]

    slug = models.SlugField(
        allow_unicode=True,
        unique=True,
        verbose_name=_("Slug"),
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Name"),
    )

    panels = [FieldPanel("name"), InlinePanel("terms", label=_("Classifier Terms"))]

    def save(self, *args, **kwargs):
        if not self.slug:
            # Make a slug and suffix a number if it already exists to ensure uniqueness
            newslug = slugify(self.name, allow_unicode=True)
            tmpslug = newslug
            suffix = 1
            while True:
                if not Classifier.objects.filter(slug=tmpslug).exists():
                    self.slug = tmpslug
                    break
                tmpslug = f"{newslug}-{str(suffix)}"
                suffix += 1
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ClassifierTerm(Orderable, models.Model):
    """
    Term used to categorize a page.
    """

    class Meta:
        verbose_name = _("Classifier Term")
        verbose_name_plural = _("Classifier Terms")

    classifier = ParentalKey(
        Classifier,
        related_name="terms",
        verbose_name=_("Classifier"),
    )
    slug = models.SlugField(
        allow_unicode=True,
        unique=True,
        verbose_name=_("Slug"),
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Name"),
    )

    panels = [
        FieldPanel("name"),
    ]

    def save(self, *args, **kwargs):
        if not self.slug:
            # Make a slug and suffix a number if it already exists to ensure uniqueness
            newslug = slugify(self.name, allow_unicode=True)
            tmpslug = newslug
            suffix = 1
            while True:
                if not ClassifierTerm.objects.filter(slug=tmpslug).exists():
                    self.slug = tmpslug
                    break
                tmpslug = f"{newslug}-{str(suffix)}"
                suffix += 1
        return super().save(*args, **kwargs)

    def __str__(self):
        return "{0} > {1}".format(self.classifier.name, self.name)


@register_snippet
class Navbar(models.Model):
    """
    Snippet for site navigation bars (header, main menu, etc.)
    """

    class Meta:
        verbose_name = _("Navigation Bar")

    name = models.CharField(
        max_length=255,
        verbose_name=_("Name"),
    )
    custom_css_class = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Custom CSS Class"),
    )
    custom_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Custom ID"),
    )
    menu_items = CjkcmsStreamField(
        NAVIGATION_STREAMBLOCKS,
        verbose_name=_("Navigation links"),
    )

    panels = [
        FieldPanel("name"),
        MultiFieldPanel(
            [
                FieldPanel("custom_css_class"),
                FieldPanel("custom_id"),
            ],
            heading=_("Attributes"),
        ),
        FieldPanel("menu_items"),
    ]

    def __str__(self):
        return self.name


@register_snippet
class Footer(models.Model):
    """
    Snippet for website footer content.
    """

    class Meta:
        verbose_name = _("Footer")

    name = models.CharField(
        max_length=255,
        verbose_name=_("Name"),
    )
    custom_css_class = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Custom CSS Class"),
    )
    custom_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Custom ID"),
    )
    content = CjkcmsStreamField(
        LAYOUT_STREAMBLOCKS,
        verbose_name=_("Content"),
    )

    panels = [
        FieldPanel("name"),
        MultiFieldPanel(
            [
                FieldPanel("custom_css_class"),
                FieldPanel("custom_id"),
            ],
            heading=_("Attributes"),
        ),
        FieldPanel("content"),
    ]

    def __str__(self):
        return self.name


@register_snippet
class ReusableContent(models.Model):
    """
    Snippet for resusable content in streamfields.
    """

    class Meta:
        verbose_name = _("Reusable Content")
        verbose_name_plural = _("Reusable Content")

    name = models.CharField(
        max_length=255,
        verbose_name=_("Name"),
    )
    content = CjkcmsStreamField(
        LAYOUT_STREAMBLOCKS, verbose_name=_("content"), use_json_field=True
    )

    panels = [FieldPanel("name"), FieldPanel("content")]

    def __str__(self):
        return self.name


@register_snippet
class Accordion(ClusterableModel):
    """Class for reusable content in a collapsible block."""

    class Meta:
        verbose_name = _("Accordion")
        verbose_name_plural = _("Accordions")

    name = models.CharField(
        max_length=255,
        verbose_name=_("Name"),
    )

    panels = [
        MultiFieldPanel(
            heading=_("Accordion"),
            children=[
                FieldPanel("name"),
            ],
        ),
        InlinePanel("accordion_panels", label=_("Panels")),
    ]

    def __str__(self):
        return self.name


class AccordionPanel(Orderable, models.Model):
    """A panel for a collapsible accordion"""

    accordion = ParentalKey(
        Accordion,
        related_name="accordion_panels",
        verbose_name=_("Accordion"),
    )

    name = models.CharField(
        max_length=255,
        verbose_name=_("Name"),
    )

    content = CjkcmsStreamField(
        HTML_STREAMBLOCKS,
        blank=True,
        use_json_field=True,
    )

    custom_css_class = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Custom CSS class"),
    )
    custom_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Custom ID"),
    )

    panels = [
        FieldPanel("custom_css_class"),
        FieldPanel("custom_id"),
        FieldPanel("name"),
        FieldPanel("content"),
    ]


class CjkcmsEmail(ClusterableModel):
    """
    General purpose abstract clusterable model used for holding email information.
    Most likely this should be subclassed with addition of a ParentalKey.
    """

    class Meta:
        abstract = True
        verbose_name = _("CMS Email")

    name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Template Name"),
    )

    to_address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("To Addresses"),
        help_text=_("Separate multiple email addresses with commas."),
    )
    from_address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("From Address"),
        help_text=_(
            'For example: "sender@example.com" or "Sender Name <sender@example.com>" (without quotes).'
        ),  # noqa
    )
    reply_address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Reply-To Address"),
        help_text=_("Separate multiple email addresses with commas."),
    )
    cc_address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("CC"),
        help_text=_("Separate multiple email addresses with commas."),
    )
    bcc_address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("BCC"),
        help_text=_("Separate multiple email addresses with commas."),
    )
    subject = models.CharField(max_length=255, blank=True, verbose_name=_("Subject"))
    body = models.TextField(blank=True, verbose_name=_("Body"))

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("to_address"),
                FieldPanel("from_address"),
                FieldPanel("cc_address"),
                FieldPanel("bcc_address"),
                FieldPanel("subject"),
                FieldPanel("body"),
            ],
            _("Email Message"),
        ),
    ]

    def __str__(self):
        return self.subject
