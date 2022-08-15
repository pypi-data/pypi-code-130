# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytest_asteroid']

package_data = \
{'': ['*']}

install_requires = \
['PyMySQL>=1.0.2,<2.0.0',
 'docker-compose>=1.29.2,<2.0.0',
 'lovely-pytest-docker==0.3.0',
 'poetry>=1.0,<2.0',
 'pytest>=6.2.5,<8.0.0']

entry_points = \
{'pytest11': ['pytest-asteroid = pytest_asteroid.asteroid']}

setup_kwargs = {
    'name': 'pytest-asteroid',
    'version': '0.4.1',
    'description': 'PyTest plugin for docker-based testing on database images',
    'long_description': '# Overview\n\n### __ASTEROID__: Automated, Solution for Testing Efficiently on Replicable, Operative, and Isolated Databases.\n\nThis pytest plugin is made for testing with MySQL docker images and is based on the great [lovely-pytest-docker](https://github.com/lovelysystems/lovely-pytest-docker "lovely-pytest-docker GitHub") plugin by Lovely Systems.\n\n__pytest-asteroid__ extends the lovely-pytest-docker plugin by adding:\n- an availability check to make sure the MySQL image is ready for connection before running the database test suite.\n- a simple reset state functionality to handle state dependency issues between tests.\n\n---\n## How do I get set up?\n\n### Dependencies\nMake sure your system has [Docker Engine](https://docs.docker.com/engine/install/) installed and that the docker daemon is running before executing your tests.\n\n### Installation\n\nInstall __pytest-asteroid__ using pip or poetry. We prefer to use [poetry](https://python-poetry.org/) as it reduces the amount of files needed in the project and simplifies dependency management and virtual environments.\n\n_Install with poetry:_\n```shell\n$ poetry add pytest-asteroid --dev\n```\n\n---\n## Examples of usage\n\nIn order to use ASTEROID make sure to have the following environmental variables set for the test DB docker image:\n* MYSQL_DATABASE\n* MYSQL_ROOT_PASSWORD\n\n#### Using the get_docker_db_port fixture\n```python\n# content from conftest.py\n\n###############################################################################\n# * Connection to test database\n# This fixture uses the ASTEROID fixture get_docker_db_port which, on first\n# session-scoped call, will envoke the docker_service startup.\n###############################################################################\n# Overwrite this fixture if a custom connection type is required\n###############################################################################\n\n\n# NOTE: Here we are using class fixture as we need the connection to close again\n# after each test class run if we want to reset state.\n# If attemting to reset state, while a connection is open,\n# we will have a deadlock.\n@pytest.fixture(scope="class")\ndef get_connection(get_docker_db_port):\n    conn = pymysql.connect(\n        database=os.environ["MYSQL_DATABASE"],\n        port=get_docker_db_port("mysql_db", timeout=30.0),\n        user="root",\n        password=os.environ["MYSQL_ROOT_PASSWORD"],\n        cursorclass=pymysql.cursors.DictCursor,\n    )\n    # Start a transaction and rollback to reset state after each test class execution\n    yield conn\n    conn.close()\n\n```\n\n#### Using the get_connection and reset_or_save_db_state fixtures\n```python\n# content from test_state.py\n\nclass TestSaveState:\n    # Test cases to check reset state works\n\n    def test_connection_insert(self, get_connection, reset_or_save_db_state):\n        reset_or_save_db_state("mysql_db", "superheroes")\n\n        conn = get_connection\n        # setup: insert new data\n        with conn.cursor() as cur:\n            cur.execute(\n                """\n                INSERT INTO superheroes (name, cape, height_cm, weigth_kg)\n                VALUES(\'Dr. Strange\', true, 188, 82)\n                """\n            )\n            conn.commit()\n            cur.execute("SELECT * FROM superheroes WHERE name = \'Dr. Strange\'")\n            rows = cur.fetchall()\n            assert len(rows) == 1\n\n```\n\n### Clarification\nUse the examples in the project repository folder _*tests/*_ for inspiration on how to use __pytest-asteroid__ and to see examples of test file structure.\n',
    'author': 'Emil Buus Sauer-Strømberg',
    'author_email': 'emil.sauer@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/stabtazer/pytest-asteroid',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
