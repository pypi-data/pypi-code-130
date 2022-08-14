from setuptools import setup

PACKAGE_NAME = "django-transactional-notifications"
PACKAGE_DESCRIPTION = "Send transactional notifications to any service."
PACKAGE_URL = "https://gitlab.com/rogeliomtx/django-notifications"
__version__ = "0.2.2"


setup(
    name=PACKAGE_NAME,
    version=__version__,
    description=PACKAGE_DESCRIPTION,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Rogelio Martínez",
    author_email="hi@rogermx.com",
    url="https://gitlab.com/rogeliomtx/django-notifications",
    install_requires=[
        "django>=2.2",
        "swapper",
        "markdown",
        "beautifulsoup4",
    ],
    test_requires=[
        "django>=2.2",
        "swapper",
        "markdown",
        "beautifulsoup4",
    ],
    packages=[
        "notifications",
        "notifications.base",
        "notifications.handlers",
        "notifications.templatetags",
        "notifications.migrations",
        "notifications.tests",
        "notifications.config",
    ],
    package_data={
        "notifications": [
            "templates/notifications/*.html",
            "static/notifications/*.js",
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 4.0",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Utilities",
    ],
    keywords="django notifications email twilio mailgun",
    license="MIT",
)
