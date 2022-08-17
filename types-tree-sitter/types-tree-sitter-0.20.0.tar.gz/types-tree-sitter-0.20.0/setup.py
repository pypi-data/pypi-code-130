from setuptools import setup

name = "types-tree-sitter"
description = "Typing stubs for tree-sitter"
long_description = '''
## Typing stubs for tree-sitter

This is a PEP 561 type stub package for the `tree-sitter` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `tree-sitter`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/tree-sitter. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `c9ebeb501c6e982de607e78cb20d7be8920a241a`.
'''.lstrip()

setup(name=name,
      version="0.20.0",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/tree-sitter.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['tree_sitter-stubs'],
      package_data={'tree_sitter-stubs': ['__init__.pyi', 'binding.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
