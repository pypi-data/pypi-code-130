#!/usr/bin/python3
# file: theme.py
# content:
# created: 2020 April 05
# modified:
# modification:
# author: roch schanen
# website: https://github.com/RochSchanen/
# comment:

# to do: inlcude more case in the argument list

# The role of imageCollect is to collect a list
# of references to the images found in a png file
# and defined in the png.txt file

# the role of imageSelect is to select from the image
# collection only the images that are necessary for
# a specific object. this selection is performed by
# building a list a pointer to the images

# to revise: does the collection need to be filled
# in parts as more images get requested: the goal
# is to limit the memory usage of applications.

# wxpython: https://www.wxpython.org/
from wx import Bitmap          as wxBitmap
from wx import BITMAP_TYPE_PNG as wxBITMAP_TYPE_PNG
from wx import Rect            as wxRect

# sys
from sys import path as syspath

# os.path
from os.path import isfile as osisfile

# path to application
_APP_PATH = syspath[0]

# list of paths to resource folders
# the last path added has precedence: this way,
# a user can easily add his own config files
_PATHS = [
    f'{_APP_PATH}/resources',   # app resources directory
    f'{_APP_PATH}',             # app local directory
    ]

# debug switch
_DEBUG = False
def DEBUG(switch):
    if switch in ["ON", "On", "on", True, 1]:
        _DEBUG = True
    if switch in ["OFF", "Off", "off", False, 0]:
        _DEBUG = False  
    if _DEBUG:
        print(f"DEUBUG switch is on")
        print(f"_APP_PATH: {_APP_PATH}")
        print(f"_PATHS:")
        for p in _PATHS:
            print(f"{' ':3}{p}")
    return

# get a valid path
def _findpath(path):
    filepath = None
    if osisfile(path):
        # the path points to a valid
        # file name, use this path
        filepath = path
    else:
        # look for all paths pointing
        # to a valid file name
        # keep the last name found
        # if no valid name is found
        # the function returns "None"        
        for p in _PATHS:
            fp = f"{p}/{path}" 
            if osisfile(fp):
                filepath = fp
    return filepath

# collect a png list
def _findpngs(name, *args):

    # load definition file
    f = open(_findpath(f'{name}.png.txt'))
    if not f: return None
    t = f.read()
    f.close()

    # get lib definitions
    library = []
    for s in t.split('\n'):
        if not s: continue               # skip empty line
        if s.strip()[0] == '#': continue # skip commnent
        l = s.split(',')                 # parse at coma
        # extract values
        offset   = int(l[0]), int(l[1]) # offset values
        grid     = int(l[2]), int(l[3]) # grid values
        size     = int(l[4]), int(l[5]) # size values
        position = int(l[6]), int(l[7]) # position values
        # build tags list
        taglist = []
        for t in l[8:]:
            taglist.append(t.strip())
        # group geometric parameters
        geometry = offset, grid, size, position
        # record all parameters
        library.append((geometry, taglist))

    # collect pngs using taglist as filter
    collection = []
    for i in library:
        geometry, taglist = i
        # filter
        valid = True
        for a in args:
            if a not in taglist:
                valid = False
        # add item to collection
        if valid:
            # remove filter tags from taglist
            for a in args:
                taglist.remove(a)
            # collect
            collection.append((geometry, taglist))
    # done
    return collection

# extract and collect bitmaps from a png file
def imageCollect(name, *args):

    # check image filepath
    fp = _findpath(f'{name}.png')
    if _DEBUG: print(f"filepath {fp}")
    if not fp: return None

    # load bitmap file
    bm = wxBitmap(fp, wxBITMAP_TYPE_PNG)
    if _DEBUG: print(f"bitmap {bm}")

    # get image collection
    collection = _findpngs(name, *args)
    if _DEBUG: print(f"collection {collection}")
    if not collection: return None

    images, taglists = [], []

    for geometry, taglist in collection:

        # get geometry
        offset, grid, size, position = geometry
        
        # get parameters
        W, H = bm.GetSize()
        X, Y = offset
        p, q = grid
        w, h = size
        m, n = position
        
        # compute grid size
        P, Q = W/p, H/q
        
        # compute clipping origin
        x = (m-1)*P + (P-w)/2 + X
        y = (n-1)*Q + (Q-h)/2 + Y
        
        # set clipping geometry
        Clip = wxRect(x, y, w, h)
        
        # clip and record
        images.append(bm.GetSubBitmap(Clip))
        taglists.append(taglist)

    # one image in the list
    if len(images) == 1:
        return images[0]

    subCollection = []
    # make image list
    for i, t in zip(images, taglists):
        subCollection.append((i, t))

    # done
    return subCollection

def imageSelect(collection, *args):

    # possible optional arguments:
    # None (all images are returned)
    # tags (images returned are filtered)
    # tags and a taglist (images are filtered and ordered)

    subCollection = []

    # filter images
    for image, taglist in collection:

        # the taglist object is to be
        # left unchanged at the end of
        # the function call
        taglistCopy = taglist.copy()
        
        valid = True
        for a in args:
            if isinstance(a, list):
                break
            if a not in taglistCopy:
                valid = False            
        if valid:
            for a in args:
                if not isinstance(a, list):
                    taglistCopy.remove(a)
            subCollection.append((image, taglistCopy))

    images = []

    # look for an ordered list
    if args:
        if isinstance(args[-1], list):
            for a in args[-1]:
                for i, t in subCollection:
                    if a in t:
                        images.append(i)
            # done
            return images

    # return all images
    for i, t in subCollection:
        images.append(i)

    # done
    return images

# -------------------------------------------------------------

if __name__ == "__main__":

    import sys

    print(f"file: {_APP_PATH}/theme.py")
    print("from package: 'pyvigi'")
    print("content:")
    print("created: 2020 04 05")
    print("author: Roch Schanen")
    print("comment:")
    print("run Python3:" + sys.version)

    # list available ressources when direclty called
