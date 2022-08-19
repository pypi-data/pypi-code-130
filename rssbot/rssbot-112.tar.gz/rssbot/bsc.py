# pylint: disable=E1101,C0116,R0912,R0915,C0115,R0903,W0212,R0902
# This file is placed in the Public Domain.


"basic"


import time


from .hdl import Commands, starttime
from .tmr import elapsed


def cmd(event):
    event.reply(",".join(sorted(Commands.cmd)))


def upt(event):
    event.reply(elapsed(time.time()-starttime))


def ver(event):
    event.reply("BOTLIB 163")
