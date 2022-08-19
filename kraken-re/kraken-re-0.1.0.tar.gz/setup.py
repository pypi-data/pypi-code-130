# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['re', 're.util']

package_data = \
{'': ['*']}

install_requires = \
['typeapi>=0.2.1,<0.3.0']

setup_kwargs = {
    'name': 'kraken-re',
    'version': '0.1.0',
    'description': '',
    'long_description': '# kraken-re\n\n(Work in progress)\n\nThe `kraken-re` provides a rule engine to describe the components of a project. These components are translated into\nbuild tasks using various rules.\n\n_The rule engine is strongly inspired by [Pants](https://www.pantsbuild.org/docs/rules-api-and-target-api)._\n\n## Concepts\n\n### Targets\n\nA Target is an addressable set of metadata. The metadata is comprised of *fields*. Each field is of a particular type,\nand no two fields can be of the same type (subclasses of another field type are accepted).\n\n### Field\n\nA Field is a strongly typed description of a piece of data, such as "PythonProjectSourceDirectory". A field may be a\nsubclass of another field, allowing it to be taken into consideration when a generic request of fields matching its\nparent class is requested.\n\n### Rules\n\nA rule describes how to translate a set of input types to an output type. Often, the inputs and output types will be\ntargets, but they can be arbitrary Python types. Every session begins with a set of initial objects that are usually\ncreated by a script.\n\nEvery object in the rule system must be immutable and hashable. If two rules produce the same result, the results\nare merged.\n\n__Example script__\n\n```py\ndocker_grpc_rust_template(name="template")\ndocker_image(dockerfile_target=":template", platforms=["linux/arm64", "linux/amd64"])\n```\n\n__Example rules__\n\n```py\n@rule\ndef get_dockerfile_resource_from_grpc_rust_template(request: DockerGrpcRustTemplateRequest) -> DockerfileResource:\n    ...\n    return DockerfileResource(path_to_dockerfile)\n\n@rule\ndef get_docker_build_requests(image: DockerImageTarget) -> DockerBuildRequests:\n    ...\n    for platform in image[DockerPlatforms]:\n        requests.append(...)\n    return DockerBuildRequests(requests)\n\n@rule\ndef build_docker(request: DockerBuildRequest) -> DockerBuildResult:\n    ...\n    return DockerBuildResult(...)\n```\n\n',
    'author': 'Niklas Rosenstein',
    'author_email': 'rosensteinniklas@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
