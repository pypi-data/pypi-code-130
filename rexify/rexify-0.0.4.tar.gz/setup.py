# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rexify',
 'rexify.components.index',
 'rexify.components.load',
 'rexify.components.retrieval',
 'rexify.components.train',
 'rexify.exceptions',
 'rexify.features',
 'rexify.models']

package_data = \
{'': ['*'], 'rexify': ['components/copy/*', 'components/download/*']}

install_requires = \
['kfp>=1.8.0,<2.0.0',
 'pandas>=1.4.0,<2.0.0',
 'scikit-learn>=1.0.0,<2.0.0',
 'tensorflow_recommenders>=0.3.0']

extras_require = \
{':sys_platform != "darwin"': ['tensorflow>=2.6.0,<3.0.0',
                               'scann>=1.2.0,<2.0.0'],
 ':sys_platform == "darwin"': ['tensorflow_metal>=0.5.0,<0.6.0',
                               'tensorflow_macos>=2.6.0,<3.0.0']}

setup_kwargs = {
    'name': 'rexify',
    'version': '0.0.4',
    'description': 'Streamlined Recommender System workflows with TensorFlow and Kubeflow',
    'long_description': '<p align="center">\n    <br>\n    <img src="https://storage.googleapis.com/rexify/1659986918545.png" height="200"/>\n    <br>\n<p>\n\n<p align="center">\n    <a href="https://circleci.com/gh/joseprsm/rexify">\n        <img alt="Build" src="https://img.shields.io/circleci/build/github/joseprsm/rexify?style=flat-square">\n    </a>\n    <a href="https://github.com/joseprsm/rexify/blob/main/LICENSE">\n        <img alt="License" src="https://img.shields.io/github/license/joseprsm/rexify?style=flat-square">\n    </a>\n    <a href="https://rexify.readthedocs.io">\n        <img alt="Documentation" src="https://img.shields.io/badge/documentation-online-success?style=flat-square">\n    </a>\n    <a href="https://pypi.org/project/rexify/">\n        <img alt="GitHub release" src="https://img.shields.io/github/v/release/joseprsm/rexify?style=flat-square">\n    </a>\n</p>\n\nRexify is a library to streamline recommender systems model development. It is built on\ntop of [Tensorflow Recommenders](https://github.com/tensorflow/recommenders) models and \n[Kubeflow](https://github.com/kubeflow/pipelines) pipelines.\n\nIn essence, Rexify adapts dynamically to your data, and outputs high-performing TensorFlow\nmodels that may be used wherever you want, independently of your data. Rexify also includes\nmodules to deal with feature engineering as Scikit-Learn Transformers and Pipelines.\n\nWith Rexify, users may easily train Recommender Systems models, just by specifying what their\ndata looks like. Rexify also comes equipped with pre-built machine learning pipelines which can\nbe used serverlessly. \n\n## What is Rexify?\n\nRexify is a low-code personalization tool, that makes use of traditional machine learning \nframeworks, such as Scikit-Learn and TensorFlow, and Kubeflow to create scalable Recommender Systems\nworkflows that anyone can use.\n\n### Who is it for?\n\nRexify is a project that simplifies and standardizes the workflow of recommender systems. It is \nmostly geared towards people with little to no machine learning knowledge, that want to implement\nsomewhat scalable Recommender Systems in their applications.\n\n## Installation\n\nThe easiest way to install Rexify is via `pip`:\n\n```shell\npip install rexify\n```\n\n## Quick Tour\n\nRexify is meant to be usable right out of the box. All you need to set up your model is interaction data - something that kind of looks like this:\n\n| user_id | item_id | timestamp  | item_name   | event_type  |\n|---------|---------|------------|-------------|-------------|\n| 22      | 67      | 2021/05/13 | Blue Jeans  | Purchase    |\n| 37      | 9       | 2021/04/11 | White Shirt | Page View   |\n| 22      | 473     | 2021/04/11 | Red Purse   | Add to Cart |\n| ...     | ...     | ...        | ...         | ...         |\n| 358     | 51      | 2021/04/11 | Bracelet    | Purchase    |\n\nAdditionally, we\'ll have to have configured a schema for the data.\nThis schema is what will allow Rexify to generate a dynamic model and preprocessing steps.\nThe schema should be comprised of three dictionaries: `user`, `ìtem`, `context`.\n\nEach of these dictionaries should consist of features and internal data types, \nsuch as: `id`, `categorical`, `timestamp`, `text`. More data types will be available \nin the future.\n\n```json\n{\n  "user": {\n    "user_id": "id"\n  },\n  "item": {\n    "item_id": "id",\n    "timestamp": "timestamp",\n    "item_name": "text"\n  },\n  "context": {\n    "event_type": "categorical"\n  }\n}\n```\n\nEssentially, what Rexify will do is take the schema, and dynamically adapt to the data.\n\n### As a package\n\nThere are two main components in Rexify workflows: `FeatureExtractor` and `Recommender`.\n\nThe `FeatureExtractor` is a scikit-learn Transformer that basically takes the schema of the data, and transforms the event data accordingly. Another method `.make_dataset()`, converts the transformed data into a `tf.data.Dataset`, all correctly configured to be fed to the `Recommender` model.\n\n`Recommender` is a `tfrs.Model` that basically implements the Query and Candidate towers. During training, the Query tower will take the user ID, user features, and context, to learn an embedding; the Candidate tower will do the same for the item ID and its features. \n\nMore information about how the `FeatureExtractor` and the `Recommender` works can be found [here](https://rexify.readthedocs.io/en/latest/overview/architecture.html). \n\nA sample Rexify workflow should sort of look like this:\n\n````python\nimport json\nimport pandas as pd\n\nfrom rexify.features import FeatureExtractor \nfrom rexify.models import Recommender\n\nevents = pd.read_csv(\'path/to/events/data\')\nwith open(\'path/to/schema\') as f:\n    schema = json.load(f)\n\nfeat = FeatureExtractor(schema)\nds = feat.fit_transform(events).batch(512)\n\nmodel = Recommender(**feat.model_params)\nmodel.compile()\nmodel.fit(ds)\n````\n\nWhen training is complete, you\'ll have a trained `tf.keras.Model` ready to be used, as you normally would. \n\n### As a prebuilt pipeline\n\nAfter cloning this project and setting up the necessary environment variables, you can run:\n\n```shell\npython -m rexify.pipeline\n```\n\nWhich should output a `pipeline.json` file. You can then upload this file manually to \neither a Kubeflow Pipeline or Vertex AI Pipelines instance, and it should run seamlessly. \n\nYou can also check the [Kubeflow Pipeline](https://kubeflow-pipelines.readthedocs.io/en/latest/source/kfp.client.html#kfp.Client.create_run_from_pipeline_package)\nand [Vertex AI](https://cloud.google.com/vertex-ai/docs/pipelines/run-pipeline#create_a_pipeline_run) \ndocumentation to learn how to submit these pipelines programmatically.\n\nThe prebuilt pipeline consists of 5 components:\n\n1. `download`, which downloads the event data from URLs set on the `$INPUT_DATA_URL` and `$SCHEMA_URL` environment variables\n2. `load`, which prepares the data downloaded in the previous step\n3. `train`, which trains a `Recommender` model on the preprocessed data\n4. `index`, which trains a [ScaNN](https://ai.googleblog.com/2020/07/announcing-scann-efficient-vector.html) model to retrieve the nearest neighbors\n5. `retrieval`, which basically retrieves the nearest _k_ neighbors for each of the known users\n\n\n### Via the demo application\n\nAfter cloning the project, install the demo dependencies and run the Streamlit application:\n\n```shell\npip install -r demo/requirements.txt\nstreamlit run demo/app.py\n```\n\nOr, if you\'re using docker:\n\n```shell\ndocker run joseprsm/rexify-demo\n```\n\nYou can then follow the steps here to set up your pipeline. \n\nDuring setup, you\'ll be asked to either input a publicly available dataset URL or use a sample data set.\nAfter that, you\'ll have a form to help you set up the schema for the data.\n\nFinally, after hitting "Compile", you\'ll have your Pipeline Spec ready. The resulting JSON file can then \nbe uploaded to Vertex AI Pipelines or Kubeflow, seamlessly.\n\nThe key difference from this pipeline to the prebuilt one is that instead of using the `download` \ncomponent to download the schema, it will pass it as an argument to the pipeline, and then use a `copy` \ncomponent to pass it down as an artifact.\n\n## License\n\n[MIT](https://github.com/joseprsm/rexify/blob/main/LICENSE)\n',
    'author': 'José Medeiros',
    'author_email': 'joseprsm@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
