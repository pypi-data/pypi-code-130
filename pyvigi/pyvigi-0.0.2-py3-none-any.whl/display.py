#!/usr/bin/python3
# file: display.py
# content:
# created: 2020 April 02
# modified:
# modification:
# author: roch schanen
# website: https://github.com/RochSchanen/
# comment:

# wxpython: https://www.wxpython.org/

from wx import Control              as wxControl

from wx import ID_ANY               as wxID_ANY
from wx import DefaultPosition      as wxDefaultPosition
from wx import DefaultSize          as wxDefaultSize
from wx import NO_BORDER            as wxNO_BORDER
from wx import DefaultValidator     as wxDefaultValidator

from wx import Bitmap               as wxBitmap
from wx import BufferedPaintDC      as wxBufferedPaintDC

from wx import EVT_ERASE_BACKGROUND as wxEVT_ERASE_BACKGROUND
from wx import EVT_PAINT            as wxEVT_PAINT

class bitmapControl(wxControl):

    def __init__(
        self,
        parent,
        images,
        names = None):

        # call parent __init__()
        wxControl.__init__(
            self,
            parent      = parent,
            id          = wxID_ANY,
            pos         = wxDefaultPosition,
            size        = wxDefaultSize,
            style       = wxNO_BORDER,
            validator   = wxDefaultValidator,
            name        = "")

        # PARAMETERS
        self.parent = parent

        # single image:
        if  isinstance(images, wxBitmap):
            self.images = [images]
            if isinstance(names, str):
                self.names = [names]

        # list of images
        elif isinstance(images, list):
            self.images = images
            self.names = names

        # dictionary images
        else:
            self.images = images.Values()
            self.names  = images.Keys()

        # status is an index or a name
        self.status = 0

        # get png size from first image
        w, h = self.images[self.status].GetSize()
        self.SetSize((w, h))

        # BINDINGS
        self.Bind(wxEVT_ERASE_BACKGROUND, self._onEraseBackground)
        self.Bind(wxEVT_PAINT, self._onPaint)

        # done
        return

    def _onEraseBackground(self, event):
        # bypass method: no flicker
        pass 

    def _onPaint(self, event):
        v = self.status
        if isinstance(v, int): n = v
        if isinstance(v, str): n = self.names.index(v)
        dc = wxBufferedPaintDC(self)
        dc.DrawBitmap(self.images[n], 0, 0)
        return

    def SetValue(self, Value):
        self.status = Value
        self.Refresh()
        return

    def GetValue(self):
        return self.status

if __name__ == "__main__":

    print("file: display.py (from pyvigi package)")
    print("content: ")
    print("created: 2020 03 21")
    print("author: Roch Schanen")
    print("comment:")
