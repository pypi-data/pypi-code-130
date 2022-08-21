#!/usr/bin/python3
# file: buttons.py
# content:
# created: 2020 April 03
# modified:
# modification:
# author: roch schanen
# website: https://github.com/RochSchanen/
# comment:

# to do: !!! add the full wheel control here
# (periodic or fixed boundaries)
# to do: if event.Skip() is really necessary
# then include it by default
# to do: add SetValue() to Radio, Switch, etc...
# to do: change self.evt to local evt.
# it is only used once to bind event object

# wxpython: https://www.wxpython.org/
import wx
import wx.lib.newevent

from pyvigi.display import bitmapControl
# from controls import Control
# from layout   import *

#################################################### _BTN

class _btn(bitmapControl):
    # super-seed __init__()
    def __init__(
        self,
        parent,
        images,
        names = None):
        # call parent __init__()
        bitmapControl.__init__(
            self,
            parent = parent,
            images = images,
            names  = names)
        # LOCALS
        self.radio = None
        self.ctr   = None
        self.evt   = None
        # BINDINGS
        self.Bind(wx.EVT_LEFT_DOWN,   self._onMouseDown)
        # capture double clicks events as secondary single clicks
        self.Bind(wx.EVT_LEFT_DCLICK, self._onMouseDown)
        # call child _start() method
        self._start()
        # done
        return

    # to super-seed
    def _start(self):
        pass

    # radio feature (to super-seed)
    def _clear(self):
        pass

    # on EVT_LEFT_DOWN, the event.skip()
    # method must be called to preserve
    # the focus event to be processed
    def _onMouseDown(self, event):
        event.Skip() # allow focus events
        return

    # Bind the event to the parent handler
    def BindEvent(self, handler):
        # "handler" is a reference to the handler method
        # usually defined in the parent class
        self.ctr, self.evt = wx.lib.newevent.NewEvent()
        self.GetParent().Bind(self.evt, handler)
        return

    # Sends a event to parent using "status" as parameter
    def SendEvent(self):
        if self.ctr:
            event = self.ctr(caller=self, status=self.status)
            wx.PostEvent(self.GetParent(), event)
        return

# #################################################### PUSHRELEASE

# one push to set
# one push to clear
# an event is sent in either case
# there is no undo gesture
#
# png binary weight:
# 2^0 = 1 = on
#
# png order:
# 0 = off
# 1 = on

# to do: integration in a radio group

class PushRelease(_btn):

    def _onMouseDown(self, event):
        event.Skip() # allow focus events
        self.status ^= 1
        self.Refresh()
        self.SendEvent()
        return

# #################################################### SWITCH

# send event when releasing
# one push to set
# one push to reset
# cancellation gesture: leaving without release
#
# png binary weight:
# 2^0 = 1 = on
# 2^1 = 2 = pressed
#
# png order:
# 0 = off released
# 1 = on  released
# 2 = off pressed
# 3 = on  pressed

class Switch(_btn):

    def _start(self):
        self.lock = False
        self.Bind(wx.EVT_LEFT_UP, self._onMouseUp)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._onMouseLeave)
        return

    def _onMouseDown(self, event):
        event.Skip() # allow focus events
        self.lock = True
        if self.radio:
            self.radio.Select(self)
        self.status |= 2
        self.Refresh()
        return

    def _onMouseUp(self, event):
        if self.lock:
            self.lock = False
            self.status &= 1
            self.status ^= 1
            self.Refresh()
            self.SendEvent()
        return

    def _onMouseLeave(self, event):
        if self.lock:
            self.lock = False
            self.status &= 1
            self.Refresh()
        return

    # called by radio group
    def _clear(self):
        if self.status:
            self.status = 0
            self.Refresh()
            self.SendEvent()
        return

    def SetValue(self, Value):
        self.status = Value
        self.Refresh()
        return



class Wheel(bitmapControl):

    def __init__(
        self,
        parent,
        images,
        hover = None):

        # concatenate hover images
        if hover:
            images += hover
            self.hover = True
        else:
            self.hover = False

        # call parent class __init__()
        bitmapControl.__init__(
            self,
            parent = parent,
            images = images,
            names  = None)
        
        # LOCALS
        self.rotation = +1    # direction
        self.reset = None     # cancel operation
        self.radio = None     # radio group handle
        self.ctr   = None     # control parent
        self.evt   = None     # event handler
        self.overflow = 0     # overflow flag
        self.n = len(images)  # full cycle number
        if self.hover:        # subtract hover images
            self.n >>= 1 
        
        # BINDINGS
        self.Bind(wx.EVT_ENTER_WINDOW, self._onMouseEnter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._onMouseLeave)
        self.Bind(wx.EVT_MOUSEWHEEL,   self._onMouseWheel)
        return

    def _onMouseEnter(self, event):
        # event.Skip() # unnecessary?
        # safely upgrade to hover
        m = self.status % self.n
        if self.hover: m += self.n
        # update state
        self.status = m
        # done
        self.Refresh()
        return

    def _onMouseLeave(self, event):
        # coerce to normal
        m = self.status % self.n
        # update state
        self.status = m
        # done
        self.Refresh()
        return

    def _onMouseWheel(self, event):
        # save state if cancellation
        self.reset = self.status
        self.overflow = 0
        # coerce to normal
        m = self.status % self.n
        # apply wheel action
        r = event.GetWheelRotation()
        if r > 0: self.step = +self.rotation
        if r < 0: self.step = -self.rotation
        m += self.step
        # set overflow flag
        if m < 0       : self.overflow = -1
        if m > self.n-1: self.overflow = +1
        # coerce (useful only when overflow)
        m %= self.n
        # upgrade to hover
        if self.hover:
            m += self.n
        # update state
        self.status = m
        # done
        self.SendEvent()
        # self.Refresh()
        return

    def SetRotation(self, Value):
        # +1 is forward
        # -1 is inverse
        self.rotation = Value
        return

    def SetValue(self, Value):
        # get value
        m = int(Value)
        # upgrade to hover
        if self.status > self.n:
            m += self.n
        # update
        self.status = m
        self.reset  = m
        self.Refresh()
        return

    def GetValue(self):
        return self.status % self.n

    def Reset(self):
        self.status = self.reset
        # self.Refresh()
        return

    # Bind the event to the parent handler
    def BindEvent(self, handler):
        # "handler" is a reference to the handler method
        # defined in the parent class
        self.ctr, self.evt = wx.lib.newevent.NewEvent()
        self.GetParent().Bind(self.evt, handler)
        return

    # Sends a event to parent using "caller" and status"
    # for parameters: caller refers to whom sends the event
    def SendEvent(self):
        if self.ctr:
            event = self.ctr(caller=self, status=self.status)
            wx.PostEvent(self.GetParent(), event)
        return

if __name__ == "__main__":

    print("file: buttons.py (from pyvigi package)")
    print("content: ")
    print("created: 2020 04 03")
    print("author: Roch Schanen")
    print("comment:")
