# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['fairgrad']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.17', 'torch>=1.0']

setup_kwargs = {
    'name': 'fairgrad',
    'version': '0.1.1',
    'description': '',
    'long_description': '# FairGrad: Fairness Aware Gradient Descent\n\nFairGrad, is an easy to use general purpose approach to enforce fairness for gradient descent based methods. \n\n# Getting started: \nYou can get ```fairgrad``` from pypi, which means it can be easily installed via ```pip```:\n```\npip install fairgrad\n```\n\n# Example usage \nTo use fairgrad simply replace your pytorch cross entropy loss with fairgrad cross entropy loss. \nAlongside, regular pytorch cross entropy arguments, it expects following meta data in the form of python dictionary.\n\n```\nfairness_related_arguments = {\n  \'y_train\' : All train example\'s corresponding label (np.asarray[int]).\n  \'s_train\' : All train example\'s corresponding sensitive attribute. This means if there\n            are 2 sensitive attributes, with each of them being binary. For instance gender - (male and female) and\n            age (above 45, below 45). Total unique sentive attributes are 4 (np.asarray[int]).\n  \'fairness_measure\': Currently we support "equal_odds", "equal_opportunity", and "accuracy_parity" (string). \n  \'epsilon\': The slack which is allowed for the final fairness level (float). \n  \'fairness_rate\': Parameter which intertwines current fairness weights with sum of previous fairness rates.\n}\n```\n\n```python\n# Note this is short snippet. One still needs to models and iterators.\n# Full worked out example is available here - @TODO\n\nfrom fairgrad.cross_entropy import CrossEntropyLoss\n\n# define cross entropy loss \ncriterion = CrossEntropyLoss(fairness_related_meta_data=fairness_related_meta_data)\n\n# Train loop\n\nfor inputs, labels, protected_attributes in train_iterator:\n  model.train()\n  optimizer.zero_grad()\n  output = model(inputs)\n  loss = criterion(output, labels, protected_attributes, mode=\'train\')\n  loss.backward()\n  optimizer.step()\n```\n\n# Citation\n```\n@article{maheshwari2022fairgrad,\n  title={FairGrad: Fairness Aware Gradient Descent},\n  author={Maheshwari, Gaurav and Perrot, Micha{\\"e}l},\n  journal={arXiv preprint arXiv:2206.10923},\n  year={2022}\n}\n```\n',
    'author': 'gmaheshwari',
    'author_email': 'gaurav.maheshwari@inria.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
