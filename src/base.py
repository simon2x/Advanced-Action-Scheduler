# -*- coding: utf-8 -*
"""
@author Simon Wu <swprojects@runbox.com>

Copyright (c) 2018 by Simon Wu <Advanced Action Scheduler> 

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version. 
"""

import platform
import wx
import wx.dataview
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin, CheckListCtrlMixin

PLATFORM = platform.system()

class TreeListCtrl(wx.dataview.TreeListCtrl):

    def __init__(self, parent, style=None):
        """
        Tree data format

        index = "n,n,n, ..."
        ...where the first n is a top-level parent. Subsequent n
        are children of the left n

        """

        if not style:
            style = wx.dataview.TL_CHECKBOX
        wx.dataview.TreeListCtrl.__init__(self, parent, style=style)
        
    def AppendItemToRoot(self, value):
        item = self.AppendItem(self.GetRootItem(), value)
        return item 
        
    def DeleteAllItems(self):
        if PLATFORM == "Windows":
            super(TreeListCtrl, self).DeleteAllItems()
        else:
            # workaround for GTK
            item = self.GetFirstItem()
            while item.IsOk():
                self.DeleteItem(item)
                item = self.GetFirstItem()
        
    def GetItemDepth(self, item):
        """  backwards """
        depth = 0
        while self.GetItemParent(item).IsOk():
            depth += 1
            item = self.GetItemParent(item)
        return depth - 1
        
    def GetIndexByOrder(self, item):
        """ iterate through all items until we reach the item """
        if not item.IsOk():
            return None
        
        n = 0 
        itemIter = self.GetFirstItem()
        if not itemIter.IsOk():
            return None
 
        while (itemIter != item):
            itemIter = self.GetNextItem(itemIter)
            n += 1
            if not itemIter.IsOk():
                break
        
        return n
        
    def GetItemIndex(self, item):
        """ hacky way of getting the item index """
        selection = item
        item = self.GetFirstItem()
        lastItem = item
        if not item.IsOk():
            return -1
          
        columnCount = self.GetColumnCount()
        row = 0
        depth = 0
        idx = "0"
        
        root = self.GetRootItem()
        items = []
        while item.IsOk():
            
            # first top level item
            if lastItem == item:
                idx = "0"
                row += 1
            
            # top level item
            elif self.GetItemParent(item) == root:
                idx = str(row)
                row += 1   
                
            # first child of previous item
            elif item == self.GetFirstChild(lastItem):
                # print(self.GetItemText(item, 0))
                idx += ",0"
                
            # sibling of previous item
            elif item == self.GetNextSibling(lastItem):
                idx = idx.split(",")
                next = int(idx[-1]) + 1 # ...and increment last
                idx = idx[0:-1]
                idx.append(str(next))
                idx = ",".join(idx)

            # sibling of parent
            elif item == self.GetNextSibling(self.GetItemParent(lastItem)):
                idx = idx.split(",")[:-1]
                # increment last element
                next = int(idx[-1]) + 1
                del idx[-1]
                idx.append(str(next))
                idx = ",".join(idx)
            
            else:
                for itm, itmIdx in items:
                    if self.GetNextSibling(itm) != item:
                        continue
                    idx = itmIdx.split(",")
                    next = int(idx[-1]) + 1 # ...and increment last
                    idx = idx[0:-1]
                    idx.append(str(next))
                    idx = ",".join(idx)
                    break
                        
            if item == selection:
                break
            lastItem = item
            items.append((item, idx))
            item = self.GetNextItem(item)

        return idx
    
    def GetLastChild(self, item):
        child = self.GetFirstChild(item)
        while child.IsOk():
            child = self.GetNextSibling(child)
        return child
        
    def GetLastSibling(self, item):
        while self.GetNextSibling(item).IsOk():
            item = self.GetNextSibling(item)
        return item
        
    def GetPreviousSibling(self, item):
        parent = self.GetItemParent(item)
        sib = self.GetNextItem(parent)
        if item == sib:
            return -1
        
        while self.GetNextSibling(sib) != item:
            sib = self.GetNextSibling(sib)
            
        return sib
        
    def GetSubTree(self, item):
        """ return the sub tree of schedule item """

        # we stop when item is a sibling
        selectedDepth = self.GetItemDepth(item)
        nextSib = self.GetNextSibling(item)
        if not nextSib.IsOk():
            parent = self.GetItemParent(item)
            nextSib = self.GetNextSibling(parent) #  not actually next sibling
            
        data = []
        columnCount = self.GetColumnCount()
        depth = selectedDepth
        idx = "0"

        while item.IsOk():

            d = self.GetItemDepth(item)

            # have we reached sibling
            if item == nextSib:
                break

            # selected item is first item
            if d == selectedDepth:
                pass

            # depth unchanged, item is the next sibling of previous item
            elif d == depth:
                idx = idx.split(",")
                next = int(idx[-1]) + 1 # ...and increment last
                idx = idx[0:-1]
                idx.append(str(next))
                idx = ",".join(idx)

            # a child of previous item
            elif d > depth:
                idx += ",0"

            # sibling of parent
            elif d < depth:
                idx = idx.split(",")[:depth]
                # increment last element
                next = int(idx[-1]) + 1
                del idx[-1]
                idx.append(str(next))
                idx = ",".join(idx)

            depth = d
            idxData = {}
            idxData["columns"] = {str(c): self.GetItemText(item, c) for c in range(columnCount)}
            idxData["checked"] = self.GetCheckedState(item)
            idxData["expanded"] = self.IsExpanded(item)
            idxData["selected"] = self.IsSelected(item)

            data.append((idx, idxData))
            item = self.GetNextItem(item)

        return data
    
    def GetTopLevelParent(self, item):
        while self.GetItemParent(item) != self.GetRootItem():
            item = self.GetItemParent(item)
        return item
     
    def GetTree(self):
        data = []
        item = self.GetFirstItem()
        items = []
        lastItem = item
        if not item.IsOk():
            return data
          
        columnCount = self.GetColumnCount()
        row = 0
        depth = 0
        idx = "0"
        
        root = self.GetRootItem()
        while item.IsOk():
            
            # first top level item
            if lastItem == item:
                idx = "0"
                row += 1
            
            # top level item
            elif self.GetItemParent(item) == root:
                idx = str(row)
                row += 1   
                
            # first child of previous item
            elif item == self.GetFirstChild(lastItem):
                # print(self.GetItemText(item, 0))
                idx += ",0"
                
            # sibling of previous item
            elif item == self.GetNextSibling(lastItem):
                idx = idx.split(",")
                next = int(idx[-1]) + 1 # ...and increment last
                idx = idx[0:-1]
                idx.append(str(next))
                idx = ",".join(idx)

            # sibling of parent
            elif item == self.GetNextSibling(self.GetItemParent(lastItem)):
                idx = idx.split(",")[:-1]
                # increment last element
                next = int(idx[-1]) + 1
                del idx[-1]
                idx.append(str(next))
                idx = ",".join(idx)
            
            else:
                for itm, itmIdx in items:
                    if self.GetNextSibling(itm) != item:
                        continue
                    idx = itmIdx.split(",")
                    next = int(idx[-1]) + 1 # ...and increment last
                    idx = idx[0:-1]
                    idx.append(str(next))
                    idx = ",".join(idx)
                    break
                

            idxData = {}
            idxData["columns"] = {str(c): self.GetItemText(item, c) for c in range(columnCount)}
            idxData["checked"] = self.GetCheckedState(item)
            idxData["expanded"] = self.IsExpanded(item)
            idxData["selected"] = self.IsSelected(item)

            data.append((idx, idxData))
            items.append((item, idx))
            lastItem = item
            item = self.GetNextItem(item)

        return data

    def InsertSubTree(self, previous, data):
        """ insert sub tree after previous item """

        if not data:
            return

        items = {}
        expandedItems = []

        for idx, idxData in data:

            columns = idxData["columns"]
            if "," not in idx:
                try:
                    # this ensures top level items pasted in correct order
                    previous = items[str(int(idx)-1)]
                except:
                    pass
                    
                if previous == -1:
                    item = self.PrependItem(self.GetItemParent(self.GetSelection()), columns["0"])
                elif not previous.IsOk():
                    if self.GetSelection().IsOk():
                        item = self.AppendItem(self.GetSelection(), columns["0"])
                    else:    
                        item = self.AppendItem(self.GetRootItem(), columns["0"])
                else:
                    item = self.InsertItem(self.GetItemParent(previous), previous, columns["0"])
            else:
                parent = idx.split(",")[:-1]
                parent = ",".join(parent)
                item = self.AppendItem(items[parent], columns["0"])

            for c in range(1, len(columns)):
                try:
                    self.SetItemText(items[idx], str(c), columns[c])
                except:
                    pass

            items[idx] = item

            checked = idxData["checked"]
            if checked == 1:
                self.CheckItem(item)
            else:
                self.UncheckItem(item)
            selected = idxData["selected"]
            if selected is True:
                self.Select(item)
            expanded = idxData["expanded"]
            if expanded is True:
                expandedItems.append(item)
            items[idx] = item

        for item in expandedItems:
            self.Expand(item)
    
    def IsTopLevel(self, item):
        return self.GetItemParent(item) == self.GetRootItem()
        
    def SelectItemByOrder(self, n):
        """ step through until we reach the nth item """
        # print("SelectItemByOrder", n)
        if n is None:
            return
        assert n >= 0, "Must be greater/equal to 0" 
        
        count = 0
        itemIter = self.GetFirstItem()
        # if not itemIter.IsOk():
            # return None
        # print(count, n)
        while n != count:
            itemIter = self.GetNextItem(itemIter)
            count += 1
        
        self.Select(itemIter)
        
    def SetTree(self, data):
        """ set the treelist """
        self.DeleteAllItems()
        
        if not data:
            return

        items = {}
        expandedItems = []

        for idx, idxData in data:

            columns = idxData["columns"]
            if "," not in idx:
                item = self.AppendItemToRoot(columns["0"])
            else:
                parent = idx.split(",")[:-1]
                parent = ",".join(parent)
                item = self.AppendItem(items[parent], columns["0"])

            for c in range(1, len(columns)):
                try:
                    self.SetItemText(items[idx], str(c), columns[c])
                except:
                    pass

            items[idx] = item

            checked = idxData["checked"]
            if checked == 1:
                self.CheckItem(item)
            else:
                self.UncheckItem(item)
            selected = idxData["selected"]
            if selected is True:
                self.Select(item)
            expanded = idxData["expanded"]
            if expanded is True:
                print( expanded )
                expandedItems.append(item)
            items[idx] = item

        for item in expandedItems:
            self.Expand(item)

class ToolTip(wx.ToolTip):

    def __init__(self, tip):

        wx.ToolTip.__init__(self, tip)

        self.SetDelay(50)
        self.SetAutoPop(20000)

        self.Enable(True)
        # self.SetDelay

class CheckList(wx.ListCtrl, ListCtrlAutoWidthMixin, CheckListCtrlMixin):

    def __init__(self, parent, style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|wx.LC_SINGLE_SEL):

        wx.ListCtrl.__init__(self, parent, style=style)
        # ListCtrlAutoWidthMixin.__init__(self)
        CheckListCtrlMixin.__init__(self)

    def DeselectAll(self):
        first = self.GetFirstSelected()
        if first == -1:
            return

        self.Select(first, on=0)
        item = first
        while self.GetNextSelected(item) != -1:
            item = self.GetNextSelected(item)
            self.Select(self.GetNextSelected(item), on=0)

class BaseList(wx.ListCtrl, ListCtrlAutoWidthMixin):

    def __init__(self, parent, style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|wx.LC_SINGLE_SEL):

        wx.ListCtrl.__init__(self, parent, style=style)
        ListCtrlAutoWidthMixin.__init__(self)
    
    def DeleteSelected(self):
        selected = self.GetFirstSelected()
        while selected != -1:
            self.DeleteItem(selected)
            selected = self.GetFirstSelected()
            
    def DeselectAll(self):
        first = self.GetFirstSelected()
        if first == -1:
            return

        self.Select(first, on=0)
        item = first
        while self.GetNextSelected(item) != -1:
            item = self.GetNextSelected(item)
            self.Select(self.GetNextSelected(item), on=0)
      
    def MoveSelectedItemsDown(self):
        items = []
        selected = self.GetFirstSelected()   
        while selected != -1:
            items.append(selected)
            selected = self.GetNextSelected(selected)
        
        if items == [self.GetItemCount()-1]:
            return
         
        limit = self.GetItemCount()-1
        rowBlockStart = None # consecutive selected rows
        for row in items:
            if row+1 in items:
                if rowBlockStart is None:
                    rowBlockStart = row
                continue
            if row == self.GetItemCount()-1:
                return
            
            itemText = []
            if rowBlockStart:
                for col in range(0, self.GetColumnCount()):
                    itemText.append(self.GetItemText(row+1, col))
                self.DeleteItem(row+1)
                new = self.InsertItem(rowBlockStart, itemText[0])
                rowBlockStart = None
            else:
                for col in range(0, self.GetColumnCount()):
                    itemText.append(self.GetItemText(row, col))
                self.DeleteItem(row)
                new = self.InsertItem(row+1, itemText[0])
                self.Select(new)
            
            for col in range(0, self.GetColumnCount()):
                self.SetItem(new, col, itemText[col])
                
    def MoveSelectedItemsUp(self):
        items = []
        selected = self.GetFirstSelected()   
        while selected != -1:
            items.append(selected)
            selected = self.GetNextSelected(selected)
        
        if items == [0]:
            return
            
        limit = 0
        for row in items:            
            if row == limit:
                limit += 1
                continue
            text = self.GetItemText(row)    
            self.DeleteItem(row)
            new = self.InsertItem(row-1, text)
            self.Select(new)

class InputDialog(wx.Dialog):

    def __init__(self, parent, title="", caption=""):

        wx.Dialog.__init__(self,
                           parent,
                           style=wx.DEFAULT_DIALOG_STYLE)

        self.SetTitle(title)

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # hsizer = wx.BoxSizer(wx.HORIZONTAL)
        caption = wx.StaticText(panel, label=caption)
        # hsizer.Add(caption, 0, wx.ALL|wx.EXPAND)

        self.input = wx.TextCtrl(panel, value="")

        hsizer2 = wx.BoxSizer(wx.HORIZONTAL)
        hsizer2.AddStretchSpacer()
        for label, id in [("Ok", wx.ID_OK),
                          ("Cancel", wx.ID_CANCEL)]:
            btn = wx.Button(panel, id=id, label=label)
            btn.Bind(wx.EVT_BUTTON, self.OnButton)
            hsizer2.Add(btn, 0, wx.ALL, 2)

        sizer.AddSpacer(20)
        sizer.Add(caption, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(self.input, 0, wx.ALL|wx.EXPAND, 5)
        sizer.AddStretchSpacer()
        sizer.Add(wx.StaticLine(panel), 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hsizer2, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        panel.SetSizer(sizer)

        #idx events binding
        self.input.Bind(wx.EVT_idx_UP, self.OnidxUp)

    def OnidxUp(self, event):
        idxcode = event.GetidxCode()
        if idxcode == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        elif idxcode == wx.WXK_RETURN:
            self.EndModal(wx.ID_OK)
        event.Skip()

    def GetValue(self):
        return self.input.GetValue()

    def OnButton(self, event):
        e = event.GetEventObject()
        id = e.GetId()
        self.EndModal(id)