# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pft']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.23.2,<2.0.0', 'torch>=1.12.1,<2.0.0']

setup_kwargs = {
    'name': 'pft',
    'version': '0.3.0',
    'description': 'Extract principal FFT components for features generation implemented in pytorch',
    'long_description': '# Principal Fourier Transformation (PFT)\n\n~~An implementation~~ A complete overhaul of https://github.com/eloquentarduino/principal-fft for pytorch.\n\nExtracts the principal Fourier Transform Components.\nThat is, for a set of signal data, PFT will extract the top N components for the whole dataset.\n\nTL;DR: Principal Component Analysis (PCA) for Fourier Space.\n\n## Installation\n\nWith pip...\n```\npip install pft\n```\n\n## Usage\n\n```python\n# Lets say you\'ve a dataset of transient signal data\n# For now, lets construct our own dataset with a single signal.\n\n# The signal will be a composite of many sine functions\nnum_steps = 100 # Number of temporal steps\nnum_coefs = 100 # Number of sine functions that make up our composite signal\ncoefs = torch.rand(num_coefs) * torch.linspace(0, 1, num_steps)\nfreqs = torch.rand(num_coefs) * 2 * torch.pi\n\n# Don\'t forgot the leading dimension!\n# pft expects the data to have the shape (num_of_data_samples, num_of_time_steps)\nsignal = torch.zeros((1, num_steps)) \nfor i, coef in enumerate(coefs):\n\tsignal += coef * torch.sin(freqs[i] * t)\n\n# Now lets extract 10 prinicipal Fourier coefficients\nfrom pft import pft\n\nnum_pfc = 10 # Number of principal Fourier coefficients\npfa = pft.PFT( # pfa = Principal Fourier Analysis\n\tnum_pfc,\n\tuse_torch=True, # Change to False to use numpy backend. Default is True.\n\tnorm="ortho",\t# Forward and Inverse Foureir Transform normalisation. Defaults to "ortho".\n) \npfa.fit(signal) # Calculates the prinicipal Fourier coefficients indexes.\npfc = pfa.transform(signal) # Gets the principal Fourier coefficients for this set of signals.\n\n# The indexes of the prinicipal Fourier coefficients are stored internally.\n# To get from the principal Fourier coefficients back to the transient signal\n# do the following:\n\nreconstructed_signal = pfa.ifit(pfc)\n```\n\nA few notes:\n\n- Both pytorch and numpy back-ends are supported but only pytorch is tested.\n- The leading dimension of the signal data is always the number of samples.\n',
    'author': 'Alex',
    'author_email': 'adrysdale@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/abdrysdale/principal-fft-torch',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
