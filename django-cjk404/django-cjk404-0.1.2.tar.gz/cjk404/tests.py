from unittest.case import skipUnless

from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from django.core.cache import cache
from wagtail.core.models import Site


from cjk404.middleware import (
    DJANGO_REGEX_REDIRECTS_CACHE_KEY,
    DJANGO_REGEX_REDIRECTS_CACHE_REGEX_KEY,
)
from cjk404.models import PageNotFoundEntry


class Cjk404RedirectTests(TestCase):
    def setUp(self):
        cache.delete(DJANGO_REGEX_REDIRECTS_CACHE_KEY)
        cache.delete(DJANGO_REGEX_REDIRECTS_CACHE_REGEX_KEY)

    def create_redirect(
        self,
        url,
        redirect_to_url,
        redirect_to_page=None,
        is_permanent=False,
        is_regexp=False,
    ):
        site = Site.objects.filter(is_default_site=True)[0]
        return PageNotFoundEntry.objects.create(
            url=url,
            redirect_to_url=redirect_to_url,
            redirect_to_page=redirect_to_page,
            permanent=is_permanent,
            regular_expression=is_regexp,
            site=site,
        )

    def redirect_url(
        self,
        requested_url,
        expected_redirect_url,
        status_code=None,
        target_status_code=404,
    ):
        response = self.client.get(requested_url)
        self.assertEquals(
            response.status_code,
            status_code,
            f"Response status code: {response.status_code} != {status_code}",
        )
        if status_code:
            self.assertRedirects(
                response,
                expected_redirect_url,
                status_code=status_code,
                target_status_code=target_status_code,
            )
        else:
            self.assertRedirects(response, expected_redirect_url)

    def test_model(self):
        site = Site.objects.filter(is_default_site=True)[0]
        r1 = self.create_redirect("/initial/", "/new_target/")
        self.assertEqual(r1.__str__(), "/initial/ ---> /new_target/")

    def test_redirect(self):
        pnfe = self.create_redirect("/initial/", "/new_target/", None)
        self.assertEqual(pnfe.hits, 0)
        self.redirect_url("/initial/", "/new_target/", 302)
        pnfe.refresh_from_db()
        self.assertEqual(pnfe.hits, 1)

    def test_redirect_to_existing_page(self):
        pnfe = self.create_redirect("/initial/", "/", None)
        self.assertEqual(pnfe.hits, 0)
        self.redirect_url("/initial/", "/", 302, 200)
        pnfe.refresh_from_db()
        self.assertEqual(pnfe.hits, 1)

    def test_redirect_premanent(self):
        pnfe = self.create_redirect("/initial2/", "/new_target/", None, True)
        self.assertEqual(pnfe.hits, 0)
        self.redirect_url("/initial2/", "/new_target/", 301)

    def test_regular_expression_without_wildcard(self):
        pnfe = self.create_redirect("/news/index/b/", "/new_target/")
        self.redirect_url("/news/index/b/", "/new_target/", 302)

    def test_premanent_regular_expression_without_wildcard(self):
        pnfe = self.create_redirect("/news/index/b/", "/new_target/", None, True)
        self.redirect_url("/news/index/b/", "/new_target/", 301)

    def test_regular_expression_witout_replacement(self):
        pnfe = self.create_redirect("/news/index/.*/", "/news/boo/b/")
        self.redirect_url(
            "/news/index/.*/",
            "/news/boo/b/",
            302,
        )

    # this fails, I do not know why, even though the actual redirect is correct and works ok
    def test_regular_expression_with_replacement(self):
        pnfe = self.create_redirect("/news/index/.*/", "/news/boo/$1/")
        self.redirect_url("/news/index/b/", "/news/boo/b/", 302, 404)

    # def test_fallback_redirects(self):
    #     """
    #     Ensure redirects with fallback_redirect set are the last evaluated
    #     """
    #     PageNotFoundEntry.objects.create(
    #         old_path='/project/foo',
    #         new_path='/my/project/foo')
    #
    #     PageNotFoundEntry.objects.create(
    #         old_path='/project/foo/(.*)',
    #         new_path='/my/project/foo/$1',
    #         regular_expression=True)
    #
    #     PageNotFoundEntry.objects.create(
    #         old_path='/project/(.*)',
    #         new_path='/projects',
    #         regular_expression=True,
    #         fallback_redirect=True)
    #
    #     PageNotFoundEntry.objects.create(
    #         old_path='/project/bar/(.*)',
    #         new_path='/my/project/bar/$1',
    #         regular_expression=True)
    #
    #     PageNotFoundEntry.objects.create(
    #         old_path='/project/bar',
    #         new_path='/my/project/bar')
    #
    #     PageNotFoundEntry.objects.create(
    #         old_path='/second_project/.*',
    #         new_path='http://example.com/my/second_project/bar/',
    #         regular_expression=True)
    #
    #     PageNotFoundEntry.objects.create(
    #         old_path='/third_project/(.*)',
    #         new_path='http://example.com/my/third_project/bar/$1',
    #         regular_expression=True)
    #
    #     response = self.client.get('/project/foo')
    #     self.assertRedirects(response,
    #                          '/my/project/foo',
    #                          status_code=301, target_status_code=404)
    #
    #     response = self.client.get('/project/bar')
    #     self.assertRedirects(response,
    #                          '/my/project/bar',
    #                          status_code=301, target_status_code=404)
    #
    #     response = self.client.get('/project/bar/details')
    #     self.assertRedirects(response,
    #                          '/my/project/bar/details',
    #                          status_code=301, target_status_code=404)
    #
    #     response = self.client.get('/project/foobar')
    #     self.assertRedirects(response,
    #                          '/projects',
    #                          status_code=301, target_status_code=404)
    #
    #     response = self.client.get('/project/foo/details')
    #     self.assertRedirects(response,
    #                          '/my/project/foo/details',
    #                          status_code=301, target_status_code=404)
    #
    #     response = self.client.get('/second_project/details')
    #     self.assertRedirects(response,
    #                          'http://example.com/my/second_project/bar/',
    #                          status_code=301, target_status_code=404)
    #
    #     response = self.client.get('/third_project/details')
    #     self.assertRedirects(response,
    #                          'http://example.com/my/third_project/bar/details',
    #                          status_code=301, target_status_code=404)
