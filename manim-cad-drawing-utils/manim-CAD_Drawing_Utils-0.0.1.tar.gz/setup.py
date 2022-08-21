# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['manim_cad_drawing_utils']

package_data = \
{'': ['*']}

install_requires = \
['bezier', 'manim>=0.15.2', 'scipy']

entry_points = \
{'manim.plugins': ['manim_cad_drawing_utils = manim_cad_drawing_utils']}

setup_kwargs = {
    'name': 'manim-cad-drawing-utils',
    'version': '0.0.1',
    'description': 'A collection of utility functions to for creating CAD-like visuals in Manim.',
    'long_description': "# Manim CAD drawing utils\n\nThis is a collecion of various functions and utilities that help creating manimations that look like CAD drawings.\nAlso some other stuff that just looks cool.\n\nFeatures:\n- Round corners\n- Chamfer corners\n- Dimensions\n- Dashed line, dashed mobject\n- Path offset mapping\n\n\n## Installation\n`manim-CAD_Drawing_Utils` is a package on pypi, and can be directly installed using pip:\n```\npip install manim-CAD_Drawing_Utils\n```\nNote: `CAD_Drawing_Utils` uses, and depends on SciPy and Manim.\n\n## Usage\nMake sure include these two imports at the top of the .py file\n```py\nfrom manim import *\nfrom manim_cad_drawing_utils import *\n```\n\n# Examples\n\n## rounded corners \n\n```py\nclass Test_round(Scene):\n    def construct(self):\n        mob1 = RegularPolygon(n=4,radius=1.5,color=PINK).rotate(PI/4)\n        mob2 = Triangle(radius=1.5,color=TEAL)\n        # making a cross\n        crbase = Rectangle(height=0.5,width=3)\n        mob3 = Union(crbase.copy().rotate(PI/4),crbase.copy().rotate(-PI/4),color=BLUE)\n        mob4 = Circle(radius=1.3)\n        mob2.shift(2.5*UP)\n        mob3.shift(2.5*DOWN)\n        mob1.shift(2.5*LEFT)\n        mob4.shift(2.5*RIGHT)\n\n        mob1 = round_corners(mob1, 0.25)\n        mob2 = round_corners(mob2, 0.25)\n        mob3 = round_corners(mob3, 0.25)\n        self.add(mob1,mob2,mob3,mob4)\n```\n![rounded_corners](/media/examples/round_corners.png)\n\n## cut off corners\n\n```py\nclass Test_chamfer(Scene):\n    def construct(self):\n        mob1 = RegularPolygon(n=4,radius=1.5,color=PINK).rotate(PI/4)\n        mob2 = Triangle(radius=1.5,color=TEAL)\n        crbase = Rectangle(height=0.5,width=3)\n        mob3 = Union(crbase.copy().rotate(PI/4),crbase.copy().rotate(-PI/4),color=BLUE)\n        mob4 = Circle(radius=1.3)\n        mob2.shift(2.5*UP)\n        mob3.shift(2.5*DOWN)\n        mob1.shift(2.5*LEFT)\n        mob4.shift(2.5*RIGHT)\n\n        mob1 = chamfer_corners(mob1, 0.25)\n        mob2 = chamfer_corners(mob2,0.25)\n        mob3 = chamfer_corners(mob3, 0.25)\n        self.add(mob1,mob2,mob3,mob4)\n\n```\n![cutoff_corners](/media/examples/cutoff_corners.png)\n\n## pointer\n\n```py\nclass test_dimension_pointer(Scene):\n    def construct(self):\n        mob1 = round_corners(Triangle().scale(2),0.3)\n        p = ValueTracker(0)\n        dim1 = Pointer_To_Mob(mob1,p.get_value(),r'triangel')\n        dim1.add_updater(lambda mob: mob.update_mob(mob1,p.get_value()))\n        dim1.update()\n        PM = Path_mapper(mob1)\n        self.play(Create(mob1),rate_func=PM.equalize_rate_func(smooth))\n        self.play(Create(dim1))\n        self.play(p.animate.set_value(1),run_time=10)\n        self.play(Uncreate(mob1,rate_func=PM.equalize_rate_func(smooth)))\n        self.play(Uncreate(dim1))\n        self.wait()\n\n\n```\n![cutoff_corners](/media/examples/pointer_triangel.gif)\n\n\n## dimension\n\n```py\nclass test_dimension_base(Scene):\n    def construct(self):\n        mob1 = round_corners(Triangle().scale(2),0.3)\n        dim1 = Linear_Dimension(mob1.get_critical_point(UP),\n                                mob1.get_critical_point(DOWN),\n                                direction=RIGHT,\n                                offset=3,\n                                color=RED)\n        dim2 = Linear_Dimension(mob1.get_critical_point(RIGHT),\n                                mob1.get_critical_point(LEFT),\n                                direction=UP,\n                                offset=-3,\n                                color=RED)\n\n        self.add(mob1,dim1,dim2)\n\n\n```\n![cutoff_corners](/media/examples/dimension.png)\n\n## hatching\n\n```py\nclass test_hatch(Scene):\n    def construct(self):\n        mob1 = Star().scale(2)\n        hatch1 = Hatch_lines(mob1,angle=PI/6,stroke_width=2)\n        hatch2 = Hatch_lines(mob1,angle=PI/6+PI/2,stroke_width=2)\n        self.add(mob1,hatch1,hatch2)\n\n\n```\n![cutoff_corners](/media/examples/hatches.png)\n",
    'author': 'GarryBGoode',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/GarryBGoode/Manim_CAD_Drawing_utils',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
