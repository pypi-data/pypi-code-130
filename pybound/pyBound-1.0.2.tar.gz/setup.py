# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pybound']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pybound',
    'version': '1.0.2',
    'description': 'pyBound is a collection of useful functions that can be used in many situations in python files.',
    'long_description': '# pyBound\n\nAllows you to access multiple useful tools in your python code quick and easy.\n\n---\n### Documentation:\n\n - clear() - clears terminal\n\n - wait(time=___) - pauses code for number for seconds inputed\n```\nprint("Hello, welcome to pyBound!")\nprint("This is some extra text!")\nwait(4)\n```\nwill display:\n```\nHello, welcome to pyBound!\nThis is some extra text!\n```\nfor 4 seconds, and then will clear the terminal and the final output will be:\n```\n```\n\n - slow_print(*strings, \ntime=___\n, end=___\n, sep=___\n, file=___) - prints text in a typing sort of animation. The time attribute defaults to a good speed, but you can change the time (in seconds) between each printed character. It will print one letter at a time.\n - rgb(r, g, b) - equate a variable to this function and just put in the rgb code of a color. When you want to change color of text, just use concatenation.\n - rgb_reset() - resets colors to white. Equate this function to a variable. Make sure to reset or the rest of you printed text will be the color it chooses\n\n```\nred = rgb(255, 0, 0)\nprint(red + "Hello, there!")\nprint("I love pyBound!")\n```\nwill print\n```\nHello there!\nI love pyBound\n```\nentirely in red. However, you can use rgb_reset() to fix this.\n\n```\nred = rgb(255, 0, 0)\nreset = rgb_reset()\nprint(red + "Hello, there!" + reset)\nprint("I love pyBound!")\n```\nwill print "Hello, there!" in red and will print "I love pyBound!" in the default terminal text color, usually white.\n\nThere are also more formatting options for your python text. They are used the same way the rgb() is used. They are listed here:\n\nend() - Deletes all existing formatting\n\nbold() - Bolds text\n\nfaint() - Decreases the opacity of text\n\nitalic() - Italicizes text\n\nunderline() - Underlines text\n\nblink_slow() - Makes text blink slowly\n\nblink_fast() - Makes text blink quickly\n\nnegative() - Inverts the background color and the foreground color of text\n\nconceal() - Makes text invisible\n\ncrossed() - Adds text strikethrough',
    'author': "Xhaiden D'Souza",
    'author_email': 'xhaidendsouza@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
