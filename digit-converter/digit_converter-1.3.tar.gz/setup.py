# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['digit_converter']
setup_kwargs = {
    'name': 'digit-converter',
    'version': '1.3',
    'description': 'A cool tool for digits converting. It could be applied in GA. It transforms a number to a list of digits under any base.',
    'long_description': "Introduction\n=============\n\n**Abstract**\n\nA cool tool for digits converting.\n\nIt could be applied in Genetic Algorithm to encode the solutions.\n\n**Keywords** Converter, Digits\n\n## Content\n\n### Classes\n\n    BaseConverter: .tonumber(lst), .tolist(num, L)\n    DigitConverter\n    BinaryConverter: subclass of DigitConverter\n    IntegerConverter: only convert integer\n    IntervalConverter: subclass of IntegerConverter, converts a number in an interval to an integer what is the index of the number then applies IntegerConverter\n\n### Objects\n\n    colorConverter: instance of BinaryConverter, transform a number (0~255) to a 8-length list of 0-1s\n    unitIntervalConverter: instance of IntervalConverter, transform a number in interval [0,1] to list of 0-1s\n\n## Grammar\n\n### import\n\n`import digit_converter`\n\n\n\n### Basic usage\n\n#### Codes\n\n```python\n    print(f'color-converter: {colorConverter.tonumber([1,0,1,0,1,1,1,0])}<->{colorConverter.tolist(174)}')\n\n    c = BinaryConverter(exponent=3)\n    d = c.tolist(12.223, L=8)\n    print(f'binary-converter: {d}<->{c.tonumber(d)}={c.pretty(d)}')\n\n    c = IntervalConverter(lb=0, ub=10)\n    d = c.tolist(2.4, L=8)\n    print(f'[{c.lb},{c.ub}]-converter: {d}<->{c(d)} -> {c.pretty(d)}-th number')\n\n    c = DigitConverter(base=16)\n    d = c.tolist(2.4, L=8)\n    print(f'16-converter: {d}<->{c(d)}={c.pretty(d)}')\n```\n\n *OUTPUT:*\n\n    color-converter: 174<->[1, 0, 1, 0, 1, 1, 1, 0]\n    binary-converter: [1, 1, 0, 0, 0, 0, 1, 1]<->12.1875=2^{3} + 2^{2} + 2^{-3} + 2^{-4}\n    [0,10]-converter: [0, 0, 1, 1, 1, 1, 0, 1]<->2.3828125 -> 2^{5} + 2^{4} + 2^{3} + 2^{2} + 2^{0}-th number\n    16-converter: [0, 2, 6, 6, 6, 6, 6, 6]<->2.399999976158142=2*16^0 + 6*16^-1 + 6*16^-2 + 6*16^-3 + 6*16^-4 + 6*16^-5 + 6*16^-6",
    'author': 'William Song',
    'author_email': '30965609+Freakwill@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Freakwill/digit_converter',
    'py_modules': modules,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
