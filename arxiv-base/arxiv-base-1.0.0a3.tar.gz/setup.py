# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['arxiv',
 'arxiv.base',
 'arxiv.base.middleware',
 'arxiv.base.tests',
 'arxiv.base.urls',
 'arxiv.base.urls.tests',
 'arxiv.forms',
 'arxiv.identifier',
 'arxiv.integration',
 'arxiv.integration.api',
 'arxiv.integration.kinesis',
 'arxiv.integration.kinesis.consumer',
 'arxiv.license',
 'arxiv.mail',
 'arxiv.mail.tests',
 'arxiv.release',
 'arxiv.release.test',
 'arxiv.status',
 'arxiv.taxonomy',
 'arxiv.util',
 'arxiv.util.tests']

package_data = \
{'': ['*'],
 'arxiv.base': ['static/css/*',
                'static/fontawesome-svgs/*',
                'static/fontawesome-svgs/svgs/brands/*',
                'static/fontawesome-svgs/svgs/solid/*',
                'static/images/*',
                'static/images/icons/*',
                'static/js/*',
                'static/sass/*',
                'static/sass/bulma/*',
                'static/sass/bulma/css/*',
                'static/sass/bulma/sass/base/*',
                'static/sass/bulma/sass/components/*',
                'static/sass/bulma/sass/elements/*',
                'static/sass/bulma/sass/grid/*',
                'static/sass/bulma/sass/layout/*',
                'static/sass/bulma/sass/utilities/*',
                'static/sass/extensions/bulma-switch/*',
                'static_test/*',
                'templates/base/*'],
 'arxiv.mail': ['templates/*', 'templates/mail/*']}

install_requires = \
['bleach',
 'boto3>=1.0.0,<2.0.0',
 'flask-s3',
 'flask>=2.2,<3.0',
 'markupsafe',
 'pytz',
 'retry',
 'semantic-version',
 'typing-extensions',
 'uwsgi',
 'wtforms']

setup_kwargs = {
    'name': 'arxiv-base',
    'version': '1.0.0a3',
    'description': 'Common code for arXiv NG',
    'long_description': None,
    'author': 'arxiv.org',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
