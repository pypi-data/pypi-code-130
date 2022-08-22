#!/usr/bin/env python

"""Required only for backward compatibility and editable installs."""

from setuptools import setup

if __name__ == "__main__":
    setup(
        use_scm_version=True,
        setup_requires=[
            "trove-classifiers",
            "setuptools_scm"
        ]
    )
