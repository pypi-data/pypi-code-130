# In the name of God
# Cearte Toolbar in Frame window
#! /usr/bin/env python
# -*- coding: utf-8 -*-

import Database.MenuSet2 as MS
from Allimp import os,sys,wx
from  Config.Init import *



class ToolData(object):
    def __init__(self):
        self.MySql = MS.GetData(u'Menu2.db', u'')
        self.ToSql = MS.SetData(u'', u'',u'')
        self.mTBarLst = {}

    def ToolBarData(self):
        self.mTBar = []
        for row in self.MySql.GetTB():
            self.mTBar.append(row)
        #return self.mTBar
    def ToolBarList(self):
        self.ToolBarData()
        for TB in self.mTBar:
            if TB[0]//100 not in self.mTBarLst:
                self.mTBarLst[TB[0]//100] = [TB]
            else:
                self.mTBarLst[TB[0]//100].append(TB)
        return self.mTBarLst


class MyToolbar(wx.ToolBar):
    data = []          #wx.TB_NODIVIDER | wx.NO_BORDER | wx.TB_FLAT |
    def __init__(self,parent,style=  wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT|wx.TB_TEXT):
        wx.ToolBar.__init__(self,parent,style=style)
        self.mytb = []


    def CreatTool(self,tbData):
        #print(tbData)
        for grp in tbData:
            for tb in tbData[grp] :
                if str(tb[1]) == '' or tb[1] == None:
                    #self.mytb.append( self.AddTool(int(tb[0]),wx.EmptyString,wx.NullBitmap,wx.NullBitmap,
                    #                           wx.ITEM_SEPARATOR,wx.EmptyString,wx.EmptyString, None) )
                    self.AddSeparator()
                elif tb[5] == 'C':
                    self.mytb.append(
                        self.AddTool(int(tb[0]), str(tb[1]), wx.Bitmap(ICONS_TOOL + tb[2], wx.BITMAP_TYPE_ANY),
                                     wx.NullBitmap, wx.ITEM_CHECK, str(tb[3]), wx.EmptyString, None)
                    )
                elif tb[5] == 'R':
                    self.mytb.append(
                        self.AddTool(int(tb[0]), str(tb[1]), wx.Bitmap(ICONS_TOOL + tb[2], wx.BITMAP_TYPE_ANY),
                                     wx.NullBitmap, wx.ITEM_RADIO, str(tb[3]), wx.EmptyString, None)
                    )
                else:
                    self.mytb.append(
                        self.AddTool(int(tb[0]), str(tb[1]),wx.Bitmap(ICONS_TOOL+tb[2], wx.BITMAP_TYPE_ANY),
                                     wx.NullBitmap, wx.ITEM_NORMAL, str(tb[3]), wx.EmptyString, None)
                    )

            self.AddSeparator()
        self.Realize()
        return self

    def GetToolid(self, id):
        return self.FindById(id)

class MyAuiToolbar(wx.aui.AuiToolBar):
    data = []
    def __init__(self, parent , style = wx.aui.AUI_TB_DEFAULT_STYLE|wx.aui.AUI_TB_GRIPPER|wx.aui.AUI_TB_PLAIN_BACKGROUND|wx.aui.AUI_TB_TEXT):
        wx.aui.AuiToolBar.__init__(self,parent,style = style )
        self.mytb = []
        self.mytp = {}
        #self.CreatTool(self.data)

    def CreatTool(self,tbData):
        for tb in tbData :
            if str(tb[1]) == '' or tb[1] == None:
                self.AddSeparator()
            else:
                self.mytb.append( self.AddTool(int(tb[0]), str(tb[1]),wx.Bitmap(ICONS_TOOL+tb[2], wx.BITMAP_TYPE_ANY),
                                               wx.NullBitmap, wx.ITEM_NORMAL, str(tb[3]), wx.EmptyString, None) )
        self.Realize()
        return self

