#!/usr/bin/env python3

from random import choice
from asciimatics.renderers import Plasma, Rainbow, FigletText
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.effects import Print
from asciimatics.exceptions import ResizeScreenError
import sys
import time


class PlasmaScene(Scene):
    _titles = [
        "ART",
    ]
    _subtitles = [
        "A Research Toolkit\nCollaborators: K. Maamari"
    ]
    _subsubtitles = [
        "Press Enter to continue"
    ]

    def __init__(self, screen):
        self._screen = screen
        effects = [
            Print(screen,
                  Plasma(int(screen.height), int(screen.width), screen.colours),
                  0,
                  speed=1,
                  transparent=False),
        ]
        super(PlasmaScene, self).__init__(effects, 50, clear=True)

    def _add_cheesy_comment(self):
        msg = FigletText(choice(self._titles), "univers")
        submsg = FigletText(choice(self._subtitles), "term")
        subsubmsg = FigletText(choice(self._subsubtitles), "term")
        self._effects.append(
            Print(self._screen,
                  msg,
                  int(self._screen.height/15),
                  x=int(self._screen.width/20),
                  colour=Screen.COLOUR_WHITE,
                  stop_frame=0,
                  speed=1))
        self._effects.append(
            Print(self._screen,
                  submsg,
                  int(self._screen.height/15)+10,
                  x=int(self._screen.width/20),
                  colour=Screen.COLOUR_WHITE,
                  stop_frame=0,
                  speed=1))
        self._effects.append(
            Print(self._screen,
                  subsubmsg,
                  int(self._screen.height*(14/15)),
                  x=int(self._screen.width/20),
                  colour=Screen.COLOUR_WHITE,
                  stop_frame=0,
                  speed=1))


    def reset(self, old_scene=None, screen=None):
        super(PlasmaScene, self).reset(old_scene, screen)

        # Make sure that we only have the initial Effect and add a new cheesy
        # comment.
        self._effects = [self._effects[0]]
        self._add_cheesy_comment()


def demo(screen):
    screen.play([PlasmaScene(screen)], stop_on_resize=True,repeat=False)
    print([PlasmaScene(screen)])

def animate():
    try:
        Screen.wrapper(demo)
        pass
    except ResizeScreenError:
        pass
