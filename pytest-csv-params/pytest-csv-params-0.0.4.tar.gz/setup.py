# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['_ptcsvp', 'pytest_csv_params']

package_data = \
{'': ['*']}

install_requires = \
['pytest>=7.1.2,<8.0.0']

entry_points = \
{'pytest11': ['pytest-csv-params = pytest_csv_params.plugin']}

setup_kwargs = {
    'name': 'pytest-csv-params',
    'version': '0.0.4',
    'description': 'Pytest plugin for Test Case Parametrization with CSV files',
    'long_description': '# pytest-csv-params\n\nA pytest plugin to parametrize tests by CSV files.\n\n## Requirements\n \n- Python 3.8, 3.9 or 3.10\n- pytest >= 7.1\n\nThere\'s no operating system dependend code in this plugin, so it should run anywhere where pytest runs.\n\n## Installation\n\nSimply install it with pip...\n\n```bash\npip install pytest-csv-params\n```\n\n... or poetry ...\n\n```bash\npoetry add --dev pytest-csv-params\n```\n\n## Usage\n\nSimply decorate your test method with `@csv_params` and the following parameters:\n\n| Parameter    | Type                     | Description                                               | Example                             |\n|--------------|--------------------------|-----------------------------------------------------------|-------------------------------------|\n| `data_file`  | `str`                    | The CSV file to use, relative or absolute path            | `/var/testdata/test1.csv`           |\n| `base_dir`   | `str` (optional)         | Directory to look up relative CSV files (see `data_file`) | `join(dirname(__file__), "assets")` |\n| `id_col`     | `str` (optional)         | Column name of the CSV that contains test case IDs        | `ID#`                               |\n| `dialect`    | `csv.Dialect` (optional) | CSV Dialect definition (see [1])                          | `csv.excel_tab`                     |\n| `data_casts` | `dict` (optional)        | Cast Methods for the CSV Data (see "Data Casting" below)  | `{ "a": int, "b": float }`          |\n\n[1] [Python CSV Documentation](https://docs.python.org/3/library/csv.html#dialects-and-formatting-parameters)\n\n### Data Casting\n\nWhen data is read from CSV, they are always parsed as `str`. If you need them in other formats, you can set a method that should be called with the value.\n\nThese methods can also be lambdas, and are also good for further transformations.\n\n#### Data Casting Example\n\n```python\nfrom pytest_csv_params.decorator import csv_params\n\ndef normalize(x: str) -> str:\n    return x.strip().upper()\n\n@csv_params(\n    data_file="/test/data.csv",\n    data_casts={\n        "col_x": normalize,\n        "col_y": float,\n    },\n)\ndef test_something(col_x, col_y):\n    # Test something...\n    ...\n```\n\n### CSV Format\n\nThe default CSV format is:\n\n- `\\r\\n` as line ending\n- All non-numeric fields are surrounded by `"`\n- If you need a `"` in the value, use `""` (double quote)\n- Fields are separated by comma (`,`)\n\n#### Example CSV\n\n```text\n"ID#", "part_a", "part_b", "expected_result"\n"first", 1, 2, 3\n"second", 3, 4, 7\n"third", 10, 11, 21\n```\n\n### Usage Example\n\nThis example uses the CSV example from above.\n\n```python\nfrom pytest_csv_params.decorator import csv_params\n\n@csv_params(\n    data_file="/data/test-lib/cases/addition.csv",\n    id_col="ID#",\n    data_casts={\n        "part_a": int,\n        "part_b": int,\n        "expected_result": int,\n    },\n)\ndef test_addition(part_a, part_b, expected_result):\n    assert part_a + part_b == expected_result\n```\n\n## Contributing\n\n### Build and test\n\nYou need [Poetry](https://python-poetry.org/) in order to build this project.\n\nTests are implemented with `pytest`, and `tox` is used to orchestrate them for the supported python versions. \n\n- Checkout this repo\n- Run `poetry install`\n- Run `poetry run tox` (for all supported python versions) or `poetry run pytest` (for your current version)\n\n### Bugs etc.\n\nPlease send your issues to `csv-params_issues` (at) `jued.de`. Please include the following:\n\n- Plugin Version used\n- Pytest version\n- Python version with operating system\n\nIt would be great if you could include example code that clarifies your issue.\n\n### Pull Requests\n\nPull requests are always welcome. Since this Gitea instance is not open to public, just send an e-mail to discuss options.\n\n## License\n\nCode is under MIT license. See `LICENSE.txt` for details.\n',
    'author': 'Juergen Edelbluth',
    'author_email': 'csv_params@jued.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://git.codebau.dev/pytest-plugins/pytest-csv-params',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
