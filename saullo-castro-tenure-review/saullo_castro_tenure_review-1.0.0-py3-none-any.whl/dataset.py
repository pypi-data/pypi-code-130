"""
Connection with Data Sets (:mod:`saullo_castro_tenure_review.dataset`)
======================================================================

.. currentmodule:: saullo_castro_tenure_review.dataset

"""
from io import BytesIO
from zipfile import ZipFile

import numpy as np
import requests


ZENODO_PREFIX = 'https://zenodo.org/record'


def is_downloadable(url):
    """Does the url contain a downloadable resource

    Solution taken from:

        https://www.codementor.io/@aviaryan/downloading-files-from-urls-in-python-77q3bs0un

    """
    h = requests.head(url, allow_redirects=True)
    header = h.headers
    content_type = header.get('content-type')
    if 'text' in content_type.lower():
        return False
    if 'html' in content_type.lower():
        return False
    return True


def zenodo_urls(doi, file_names):
    """Return the urls of file names according to https://zenodo.org/

    Parameters
    ----------
    doi: str
        The DOI of the data set.
    file_names: str or list of str
        The file names for which the urls should be obtained.

    """
    file_names = np.atleast_1d(file_names)
    reg = doi.split('.')[-1]
    urls = []
    for file_name in file_names:
        url = ZENODO_PREFIX + ('/%s/files/%s' % (reg, file_name))
        assert is_downloadable(url), 'URL %s is not downloadable' % (url)
        urls.append(url)
    return urls


def extract_files_from_urlzip(zip_url, file_names):
    """Extract a list of files from a zip file url

    Parameters
    ----------
    zip_url: str
        The zip file url.
    file_names: str or list of str
        The file names to be extracted.

    """
    file_names = np.atleast_1d(file_names)
    assert is_downloadable(zip_url), 'URL %s is not downloadable' % (zip_url)
    r = requests.get(zip_url)
    zipfile = ZipFile(BytesIO(r.content))
    success = [False]*len(file_names)
    count = 0
    for fname in zipfile.namelist():
        for file_name in file_names:
            if file_name in fname:
                zipfile.extract(fname, '.')
                success[count] = True
                count += 1
    if not sum(success) == len(file_names):
        for i, test in enumerate(success):
            if not test:
                raise RuntimeError('Could not extract file: %s' % file_names[i])


def files_from_urls(urls, file_names=None):
    """Download files from given urls

    Parameters
    ----------
    urls: list of str
        The urls of the files to be downloaded.
    file_names: str or list of str, optional
        The file names corresponding to the urls, by default it will be
        everything after the last "/" of the urls.

    """
    if file_names is None:
        file_names = [url.split('/')[-1] for url in urls]
    else:
        file_names = np.atleast_1d(file_names)
    for url, file_name in zip(urls, file_names):
        assert is_downloadable(url), 'URL %s is not downloadable' % (url)
        r = requests.get(url, allow_redirects=True)
        open('%s' % file_name, 'wb').write(r.content)
