"""Contains the PageAssetFinder"""
import os
import urllib.parse

from django.apps import apps
from django.conf import settings
from django.contrib.staticfiles import finders, utils


class PageAssetFinder(finders.BaseFinder):
    """A static asset finder based on page structure"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pageassets = {}  # pagename: storage instance
        config = settings.WEBPACK_PAGES
        self.load_pages(config["ROOT_PAGE_DIR"], namespace="root")
        for app_config in apps.get_app_configs():
            self.load_pages(os.path.join(app_config.path, "pages"), namespace=app_config.name)

    def load_pages(self, path, namespace=None):
        """Loads all pages' assets in the entire path"""
        if not os.path.exists(path):
            return
        for pagepath in os.listdir(path):
            if os.path.isdir(os.path.join(path, pagepath)) and pagepath != "assets":
                pagename = f"{namespace}.{pagepath}" if namespace else pagepath
                if os.path.exists(os.path.join(path, pagepath, "assets")):
                    self.pageassets[pagename] = finders.FileSystemStorage(os.path.join(path, pagepath, "assets"))
                    self.pageassets[pagename].prefix = self.page_asset_name(pagename, "")
                self.load_pages(os.path.join(path, pagepath), namespace=pagename)

    def check(self, **_):
        """No errors so far."""
        return []

    def list(self, ignore_patterns):
        """Lists all files"""
        for _, assetstorage in self.pageassets.items():
            if assetstorage.exists(""):
                for path in utils.get_files(assetstorage, ignore_patterns):
                    yield path, assetstorage

    def find(self, path, all=False):  # pylint: disable=redefined-builtin
        """Finds a static file with a given name"""
        pathelements = os.path.normpath(path).split(os.path.sep)
        if pathelements[0] == "assets":
            assets = self.pageassets.get(pathelements[1])
            if assets and assets.exists(os.path.join(*pathelements[2:])):
                matched_path = assets.path(os.path.join(*pathelements[2:]))
                if matched_path and not all:
                    return matched_path
                if matched_path and all:
                    return [matched_path]
        return []

    @staticmethod
    def page_asset_name(pagename, path):
        """Returns the name of a page asset, given a page name and a path"""
        return os.path.join("assets", pagename, path)

    @staticmethod
    def page_asset_url(pagename, path):
        """Returns the url of a page asset, given a page name and a path"""
        return urllib.parse.urljoin(settings.STATIC_URL, PageAssetFinder.page_asset_name(pagename, path))
