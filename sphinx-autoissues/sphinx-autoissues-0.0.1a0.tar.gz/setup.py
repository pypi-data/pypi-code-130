# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sphinx_autoissues']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'sphinx-autoissues',
    'version': '0.0.1a0',
    'description': 'Sphinx integration with different issuetrackers',
    'long_description': '#################\nsphinx_autoissues\n#################\n\n.. image:: https://secure.travis-ci.org/tony/sphinx_autoissues.png\n   :target: http://travis-ci.org/tony/sphinx_autoissues\n\nhttp://sphinx_autoissues.git-pull.com/\n\nThis is a fork of Sebastian Wiesner <lunaryorn@gmail.com>\'s excellent\nsphinxcontrib-issuetracker_ plugin.\n\n.. _sphinxcontrib-issuetracker: https://github.com/lunaryorn/sphinxcontrib-issuetracker\n\nA Sphinx_ extension to reference issues in issue trackers, either explicitly\nwith an "issue" role or optionally implicitly by issue ids like ``#10`` in\nplaintext.\n\nCurrently the following issue trackers are supported:\n\n- `GitHub <http://github.com>`_\n- `BitBucket <http://bitbucket.org>`_\n- `Launchpad <https://launchpad.net>`_\n- `Google Code <http://code.google.com>`_\n- `Debian BTS <http://bugs.debian.org>`_\n- `Jira <http://www.atlassian.com/software/jira/>`_\n\nA simple API is provided to add support for other issue trackers.  If you added\nsupport for a new tracker, please consider sending a patch to make your work\navailable to other users of this extension.\n\n\nInstallation\n------------\n\nThis extension can be installed from the `Python Package Index`_::\n\n   pip install sphinx_autoissues\n\nThis extension requires Sphinx 1.1 and Python 2.6 or Python 3.1.\n\n\nUsage\n-----\n\nJust add this extension to ``extensions`` and configure your issue tracker::\n\n   extensions = [\'sphinx_autoissues\']\n\n   issuetracker = \'github\'\n   issuetracker_project = \'tony/sphinx_autoissues\'\n\nNow issue references like ``#10`` are replaced with links to the issue tracker\nof this extension, unless the reference occurs in literal text like inline\nliterals or code blocks.\n\nYou can disable this magic behaviour by setting issuetracker_plaintext_issues\nto ``False``::\n\n   issuetracker_plaintext_issues = False\n\nNow textual references are no longer replaced. However, you can still explicitly\nreference issues with the ``issue`` role.\n\nFor more details refer to the documentation_.\n\n\nSupport\n-------\n\nPlease report issues to the `issue tracker`_ if you have trouble, found a bug in\nthis extension or lack support for a specific issue tracker, but respect the\nfollowing rules:\n\n- Check that the issue has not already been reported.\n- Check that the issue is not already fixed in the ``master`` branch.\n- Open issues with clear title and a detailed description in grammatically\n  correct, complete sentences.\n\n\nDevelopment\n-----------\n\nThe source code is hosted on Github_:\n\n   git clone https://github.com/tony/sphinx_autoissues\n\nPlease fork the repository and send pull requests with your fixes or cool new\nfeatures, but respect the following rules:\n\n- Read `how to properly contribute to open source projects on GitHub\n  <http://gun.io/blog/how-to-github-fork-branch-and-pull-request/>`_.\n- Use a topic branch to easily amend a pull request later, if necessary.\n- Write `good commit messages\n  <http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html>`_.\n- Squash commits on the topic branch before opening a pull request.\n- Respect :pep:`8` (use `pep8`_ to check your coding style compliance)\n- Add unit tests\n- Open a `pull request <https://help.github.com/articles/using-pull-requests>`_\n  that relates to but one subject with a clear title and description in\n  grammatically correct, complete sentences.\n\n\n.. _Sphinx: http://sphinx.pocoo.org/latest\n.. _documentation: http://sphinx_autoissues.readthedocs.org\n.. _Python package index: http://pypi.python.org/pypi/sphinx_autoissues\n.. _issue tracker: https://github.com/tony/sphinx_autoissues/issues/\n.. _pep8: http://pypi.python.org/pypi/pep8/\n',
    'author': 'Tony Narlock',
    'author_email': 'tony@git-pull.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://sphinx-autoissues.git-pull.com',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
