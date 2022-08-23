import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "halloumi-cross-account-parameter-store",
    "version": "1.0.0",
    "description": "A custom CDK construct to manage a parameter across an AWS account. This construct creates a Lambda-backed custom resource using AWS CloudFormation that handles assuming a role on the target AWS account and puts, updates or deletes a parameter on that account. Role and parameter related variables are passed to the construct and are used by the function to perform these operations.",
    "license": "Apache-2.0",
    "url": "https://github.com/sentialabs/halloumi-cross-account-parameter-store.git",
    "long_description_content_type": "text/markdown",
    "author": "Sentia MPC<support.mpc@sentia.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/sentialabs/halloumi-cross-account-parameter-store.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "halloumi_cross_account_parameter_store",
        "halloumi_cross_account_parameter_store._jsii"
    ],
    "package_data": {
        "halloumi_cross_account_parameter_store._jsii": [
            "halloumi-cross-account-parameter-store@1.0.0.jsii.tgz"
        ],
        "halloumi_cross_account_parameter_store": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk-lib>=2.37.1, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.65.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard~=2.13.3"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
