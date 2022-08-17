from setuptools import setup

name = "types-tree-sitter-languages"
description = "Typing stubs for tree-sitter-languages"
long_description = '''
## Typing stubs for tree-sitter-languages

This is a PEP 561 type stub package for the `tree-sitter-languages` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `tree-sitter-languages`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/tree-sitter-languages. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `2c052651e953109c94ae998f5ccc6d043df060c9`.
'''.lstrip()

setup(name=name,
      version="1.3.0",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/tree-sitter-languages.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=['types-tree-sitter'],
      packages=['tree_sitter_languages-stubs'],
      package_data={'tree_sitter_languages-stubs': ['__init__.pyi', 'core.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
