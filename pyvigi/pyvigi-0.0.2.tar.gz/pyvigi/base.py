#!/usr/bin/python3
# file: base.py
# content: define the App class
# created: 2020 03 21
# modified:
# modification:
# author: Roch Schanen
# comment:
# repository: https://github.com/RochSchanen/pyvigi_dev

# wxpython: https://www.wxpython.org/
import wx

"""
    simplified graphic interface mini library:
    
    On instantiating an "App" object, a frame is
    automatically created and a panel container
    too.
    
    The "BackgroundBitmap" variable is used to
    paint the panel background on refresh if
    the object is referenced to a bitmap object.

    The "BackgroundBitmap" is also used as a canvas
    by the layout class for drawing decorum.

"""

# simple Panel class
class _basePanel(wx.Panel):
    # super-seed the __init__ method
    def __init__(self, parent):
        # call parent class __init__()
        wx.Panel.__init__(
            self,
            parent = parent,
            id     = wx.ID_ANY,
            pos    = wx.DefaultPosition,
            size   = wx.DefaultSize,
            style  = wx.NO_BORDER,
            name   = "")
        # BackgroundBitmap
        self.BackgroundBitmap = None
        # bind paint event
        self.Bind(wx.EVT_PAINT, self._OnPaint)
        # done
        return

    # "BufferedPaintDC" or "DCPaint" : documentation required
    def _OnPaint(self, event):
        # redraw if BackgroundBitmap is defined
        if self.BackgroundBitmap: 
            dc = wx.PaintDC(self)                               # (1)
            dc.DrawBitmap(self.BackgroundBitmap, 0, 0)
        return

# simple Frame class
class _baseFrm(wx.Frame):
    # super-seed the __init__ method
    def __init__(self):
        # call parent class __init__()
        wx.Frame.__init__(
            self,
            parent = None,
            id     = wx.ID_ANY,
            title  = "",
            pos    = wx.DefaultPosition,
            size   = wx.DefaultSize,
            style  = wx.DEFAULT_FRAME_STYLE
                    ^ wx.RESIZE_BORDER
                    ^ wx.MAXIMIZE_BOX,
            name   = "")
        # Create panel
        self.Panel = _basePanel(self)
        # done
        return

# Set _ESCAPE = True allows the ESCAPE key
# to force the application to exit (debugging).
_ESCAPE = True

# simple App class
class App(wx.App):

    def OnInit(self):
        # make reference to App
        self.App = self
        # create and show Frame
        self.Frame = _baseFrm()     
        # reference to Panel
        self.Panel = self.Frame.Panel
        # call user's Start code
        self.Start()
        # adjust widow size to BackgroundBitmap size
        if self.Frame.Panel.BackgroundBitmap:
            w, h = self.Frame.Panel.BackgroundBitmap.GetSize()
            self.Frame.SetClientSize((w, h))
        # bind key event (for ESCAPE key)
        self.Bind(wx.EVT_KEY_DOWN, self._OnKeyDown)
        # show the frame
        self.Frame.Show(True)
        # done
        return True

    def Start(self):
        # here is the user's start up code
        pass

    # catch the ESCAPE key and exit the app
    # only if the _ESCAPE flag is set. This is
    # defined for development purposes and can
    # be removed or improved at later time.
    def _OnKeyDown(self, event):
        key = event.GetKeyCode()
        if _ESCAPE:
            if key == wx.WXK_ESCAPE:
                wx.Exit()
                return
        event.Skip() # forward event
        return

    # def __del__(self):
    #     return

if __name__ == "__main__":

    print("file: base.py (from pyvigi package)")
    print("content: define the App class")
    print("created: 2020 03 21")
    print("author: Roch Schanen")
    print("comment:")
