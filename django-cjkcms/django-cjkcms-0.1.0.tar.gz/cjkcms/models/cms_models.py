"""
Default creatable pages used in Cjk CMS, for jump-starting new websites 
without having to create a new page types.
Feel free to replace this file with your own configuration,
in your Wagtail project. Copy+paste and modify as needed.

There are two versions of this file: cms_models and cms_models_legacy.
The legacy version uses StreamField as body field, while the new version
uses CjkcmsStreamField, avoiding issues with migrations. See fields.py for details.
"""
from modelcluster.fields import ParentalKey
from django.utils.translation import gettext_lazy as _
from . import (
    CjkcmsArticlePage,
    CjkcmsArticleIndexPage,
    CjkcmsWebPage,
)
from cjkcms.fields import CjkcmsStreamField
from cjkcms.blocks import LAYOUT_STREAMBLOCKS, CONTENT_STREAMBLOCKS


class ArticlePage(CjkcmsArticlePage):
    """
    Article, suitable for news or blog content.
    """

    class Meta:
        verbose_name = _("Article")
        ordering = ["-first_published_at"]

    # Only allow this page to be created beneath an ArticleIndexPage.
    # parent_page_types = ['website.ArticleIndexPage']

    # Override to CjkcmsStreamField to get rid of migration issues
    # when modifying CONTENT_STREAMBLOCKS.
    body = CjkcmsStreamField(
        CONTENT_STREAMBLOCKS, null=True, blank=True, use_json_field=True
    )

    template = "cjkcms/pages/article_page.html"
    amp_template = "cjkcms/pages/article_page.amp.html"
    search_template = "cjkcms/pages/article_page.search.html"
    search_filterable = True


class ArticleIndexPage(CjkcmsArticleIndexPage):
    """
    Shows a list of article sub-pages.
    """

    # Override to CjkcmsStreamField to get rid of migration issues
    # when modifying LAYOUT_STREAMBLOCKS.
    body = CjkcmsStreamField(
        LAYOUT_STREAMBLOCKS, null=True, blank=True, use_json_field=True
    )

    class Meta:
        verbose_name = _("Article Landing Page")

    # Override to specify custom index ordering choice/default.
    index_query_pagemodel = "cjkcms.ArticlePage"

    # Only allow ArticlePages beneath this page.
    subpage_types = ["cjkcms.ArticlePage"]

    template = "cjkcms/pages/article_index_page.html"


class WebPage(CjkcmsWebPage):
    """
    General use page with featureful streamfield and SEO attributes.
    """

    # Override to CjkcmsStreamField to get rid of migration issues
    # when modifying LAYOUT_STREAMBLOCKS.
    body = CjkcmsStreamField(
        LAYOUT_STREAMBLOCKS, null=True, blank=True, use_json_field=True
    )

    class Meta:
        verbose_name = _("Web Page")

    template = "cjkcms/pages/web_page.html"
