# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cloudflare_dyndns']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=21.1.0,<22.0.0',
 'click>=7.0,<8.0',
 'httpx>=0.23.0,<0.24.0',
 'pydantic>=1.8.1,<2.0.0',
 'truststore>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['cloudflare-dyndns = cloudflare_dyndns.cli:main']}

setup_kwargs = {
    'name': 'cloudflare-dyndns',
    'version': '5.0b2',
    'description': 'CloudFlare Dynamic DNS client',
    'long_description': '# CloudFlare Dynamic DNS client\n\nThis is a simple Dynamic DNS script written in Python for updating CloudFlare DNS A records,  \nsimilar to the classic [ddclient perl script](https://sourceforge.net/p/ddclient/wiki/Home/).\n\n- You can run it as a cron job or a systemd timer.\n- It only updates the records if the IP address actually changed by storing a\n  cache of the current IP address.\n- It checks multiple IP services. If one of them doesn\'t respond, it skips it and check the next.\n- It has an easy to use command line interface.\n\n## Install\n\nYou can simply install it with pip [from PyPI](https://pypi.org/project/cloudflare-dyndns/):\n\n```bash\n$ pip install cloudflare-dyndns\n```\n\nOr you can [download a standalone binary from the releases page.](https://github.com/kissgyorgy/cloudflare-dyndns/releases/)\n\nOr you can use [the Docker image](https://hub.docker.com/r/kissgyorgy/cloudflare-dyndns):\n\n```bash\n$ docker run --rm -it kissgyorgy/cloudflare-dyndns --help\n```\n\nPlease note that before you can use the `-6` IPv6 option in Docker, you need to [enable IPv6 support in the Docker daemon](https://docs.docker.com/config/daemon/ipv6/).\nAfterward, you can choose to use either IPv4 or IPv6 (or both) with any container, service, or network.\n\n# Note\n\nIf you use this script, it "takes over" the handling of the record of those\ndomains you specified, which means it will update existing records and create\nmissing ones.\n\nYou should not change A or AAAA records manually or with other scripts, because\nthe changes will be overwritten.\n\nI decided to make it work this way, because I think most users expect this\nbehavior, but if you have a different use case,\n[let me know!](https://github.com/kissgyorgy/cloudflare-dyndns/issues/new)\n\n## Command line interface\n\n```\n$ cloudflare-dyndns --help\nUsage: cloudflare-dyndns [OPTIONS] [DOMAINS]...\n\n  A command line script to update CloudFlare DNS A and/or AAAA records based\n  on the current IP address(es) of the machine running the script.\n\n  For the main domain (the "@" record), simply put "example.com"\n  Subdomains can also be specified, eg. "*.example.com" or "sub.example.com"\n\n  You can set the list of domains to update in the CLOUDFLARE_DOMAINS\n  environment variable, in which the domains has to be separated by\n  whitespace, so don\'t forget to quote the value!\n\n  The script supports both IPv4 and IPv6 addresses. The default is to set\n  only A records for IPv4, which you can change with the relevant options.\n\nOptions:\n  --api-token TEXT   CloudFlare API Token (You can create one at My Profile\n                     page / API Tokens tab). Can be set with\n                     CLOUDFLARE_API_TOKEN environment variable.  [required]\n\n  --proxied          Whether the records are receiving the performance and\n                     security benefits of Cloudflare.\n\n  -4 / -no-4         Turn on/off IPv4 detection and set A records.\n                     [default: on]\n\n  -6 / -no-6         Turn on/off IPv6 detection and set AAAA records.\n                     [default: off]\n\n  --delete-missing   Delete DNS record when no IP address found. Delete A\n                     record when IPv4 is missing, AAAA record when IPv6 is\n                     missing.\n\n  --cache-file FILE  Cache file  [default: /home/walkman/.cache/cloudflare-\n                     dyndns/ip.cache]\n\n  --force            Delete cache and update every domain\n  --debug            More verbose messages and Exception tracebacks\n  --help             Show this message and exit.\n```\n\n## Shell exit codes\n\n- `1`: Unknown error happened\n- `2`: IP cannot be determined (IP service error)\n- `3`: CloudFlare related error (cannot call API, cannot get records, etc...)\n\n# Changelog\n\n- **v5.0** Mac OS Support\n\n  Able to read CA bundle from trust stores on Mac OS too, no need for file-based CA store.\n\n- **v4.0** IPv6 support\n\n  Now you can specify `-6` command line option to update AAAA records too.  \n  You can delete records for missing IP addresses with the `--delete-missing`\n  option. See [issue #6](https://github.com/kissgyorgy/cloudflare-dyndns/issues/6) for details.  \n  There is a new `--proxied` flag for setting Cloudflare DNS services.\n\n- **v3.0** breaks backward compatibility using the global API Key\n\n  You can only use API Tokens now, which you can create under `My Profile / API Tokens`: https://dash.cloudflare.com/profile/api-tokens.\n  The problem with the previously used API Key is that it has global access to\n  your Cloudflare account. With the new API Tokens, you can make the script\n  permissions as narrow as needed.\n\n  **Upgrading from 2.0 and using API Tokens is highly recommended!**\n\n  The `--domains` option is now gone, because it made no sense (it only existed\n  for reading from the envvar), but you can use the `CLOUDFLARE_DOMAINS` envvar\n  the same as before.\n\n- **v2.0** breaks backward compatibility for a PyPI release.\n\n  The script you need to run is now called `cloudflare-dyndns` and the cache file\n  also changed. You can delete the old cache manually, or you can leave it, it\n  won\'t cause a problem.\n\n  The Docker file entry point is changed, so if you pull the new image, everything\n  will work as before.\n\n## Development\n\nYou can install dependencies with poetry (preferable in a virtualenv).  \nAfter [installing poetry](https://poetry.eustace.io/docs/#installation), simply run:\n\n```bash\n$ poetry install\n```\n',
    'author': 'Kiss György',
    'author_email': 'kissgyorgy@me.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kissgyorgy/cloudflare-dyndns',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
