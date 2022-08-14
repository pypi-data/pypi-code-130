# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tidbcloudy', 'tidbcloudy.util']

package_data = \
{'': ['*']}

install_requires = \
['mysqlclient>=2.1.1,<3.0.0', 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'tidbcloudy',
    'version': '0.2.2',
    'description': 'Python SDK for TiDB Cloud',
    'long_description': '# Python SDK for TiDB Cloud\n\n## Introduction\n\n`tidbcloudy` is a Python package that provides a high-level interface to access TiDB Cloud.\n\n## Installation\n\n```bash\npip install tidbcloudy\n```\n\n## Usage\n\n### List all resources in your organization\n\n```python\nimport tidbcloudy\n\napi = tidbcloudy.TiDBCloud(public_key="public_key", private_key="private_key")\nfor project in api.iter_projects():\n    print(project)\n    for cluster in project.iter_clusters():\n        print(cluster)\n        for backup in cluster.iter_backups():\n            print(backup)\n    for restore in project.iter_restores():\n        print(restore)\n```\n\n### Create a cluster\n\n```python\nimport tidbcloudy\nfrom tidbcloudy.specification import CreateClusterConfig\n\napi = tidbcloudy.TiDBCloud(public_key="public_key", private_key="private_key")\nproject = api.get_project("project_id", update_from_server=True)\n\nconfig = CreateClusterConfig()\nconfig.set_name("cluster-name") \\\n    .set_cluster_type("cluster-type") \\\n    .set_cloud_provider("cloud-provider") \\\n    .set_region("region-code") \\\n    .set_port(4399) \\\n    .set_root_password("root_password") \\\n    .set_component("tidb", "8C16G", 1) \\\n    .set_component("tikv", "8C32G", 3, 500) \\\n    .add_current_ip_access()\n\ncluster = project.create_cluster(config)\ncluster.wait_for_ready()\n```\n\n### Modify a cluster\n\n```python\nimport tidbcloudy\nfrom tidbcloudy.specification import UpdateClusterConfig\n\napi = tidbcloudy.TiDBCloud(public_key="public_key", private_key="private_key")\nproject = api.get_project("project_id", update_from_server=True)\ncluster = project.get_cluster("cluster_id")\nnew_config = UpdateClusterConfig()\nnew_config.update_component("tiflash", node_quantity=1, node_size="8C64G", storage_size_gib=500)\ncluster.update(new_config)\n```\n\n### Create a backup\n\n```python\nimport tidbcloudy\n\napi = tidbcloudy.TiDBCloud(public_key="public_key", private_key="private_key")\nproject = api.get_project("project_id", update_from_server=True)\ncluster = project.get_cluster("cluster_id")\nbackup = cluster.create_backup(name="backup-1", description="created by tidbcloudy")\nprint(backup)\n```\n\n### Create a restore\n\n```python\nimport tidbcloudy\nfrom tidbcloudy.specification import CreateClusterConfig\n\napi = tidbcloudy.TiDBCloud(public_key="public_key", private_key="private_key")\nproject = api.get_project("project_id", update_from_server=True)\ncluster = project.get_cluster("cluster_id")\n\nbackup_config = CreateClusterConfig()\nbackup_config \\\n    .set_cluster_type("cluster-type") \\\n    .set_cloud_provider("cloud-provider") \\\n    .set_region("region-code") \\\n    .set_port(4399) \\\n    .set_root_password("root-password") \\\n    .set_component("tidb", "8C16G", 1) \\\n    .set_component("tikv", "8C32G", 3, 500) \\\n    .set_component("tiflash", "8C64G", 2, 500) \\\n    .add_current_ip_access()\nrestore = project.create_restore(backup_id="backup_id", name="restore-by-tidbcloudy", cluster_config=backup_config)\nprint(restore)\n```\n\n## Enhancements comparing to original TiDB Cloud API\n\n- Iterate over resources instead of manual pagination\n- Connect to a TiDB cluster using the MySQL client\n- Get a Project using a Project ID\n- Configure your cluster with method chaining\n- Add your current IP address automatically\n- Wait for the cluster to be ready when creating/modifying a cluster\n- Case-insensitive when setting cluster type, cloud provider, and component name\n',
    'author': 'Aolin',
    'author_email': 'aolinz@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
