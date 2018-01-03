import wx
import wx.dataview
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin, CheckListCtrlMixin

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
        
        # implicit root item
        self.__root = self.GetRootItem()
        
        # item reference by index
        self.__indexdict = {}
        
        # item data/state reference by index
        # self.__indexdata = {}
        
        # number of top-level items
        self.__toplevelcount = 0
     
    def GetSelection(self):
        item = super(TreeListCtrl, self).GetSelection()
        index = super(TreeListCtrl, self).GetItemData(item)

        return index
        
    def SetItemText(self, index, value):
        item = self.__indexdict[index]
        super(TreeListCtrl, self).SetItemText(item, value)

        # self.__indexdata[index]["columns"] = 
    
    def UncheckItem(self, index):
        item = self.__indexdict[index]
        super(TreeListCtrl, self).UncheckItem(item)
        
    def CheckItem(self, index):
        item = self.__indexdict[index]
        super(TreeListCtrl, self).CheckItem(item)
        
    def Expand(self, index):
        item = self.__indexdict[index]
        super(TreeListCtrl, self).Expand(item)
    
    def GetCheckedState(self, item):
        """ return checked state of given item """ 
        if isinstance(item, wx._dataview.TreeListItem):            
            return super(TreeListCtrl, self).GetCheckedState(item)
        
        assert item in self.__indexdict, "not a valid index: %s (%s)" % (str(item), type(item))        
        
        item = self.__indexdict[item]        
        return self.GetCheckedState(item)
        
    def DeleteItem(self, item):
        """ return checked state of given item """ 
        if isinstance(item, wx._dataview.TreeListItem):            
            d = {value: key for key,value in self.__indexdict.items()}
            item = d[item]
        
        assert item in self.__indexdict, "not a valid index: %s (%s)" % (str(item), type(item))        
        
        item = self.__indexdict[item]        
        self.DeleteItem(item)
        
        # we need to adjust index keys to account for the deleted item
        for k,v in self.__indexdict.items():
            if k.startswith(item):
                del self.__indexdict[k]
                
        # decrement by one for items below deleted item
        item_split = item.split(",")
        parent = item_split[:-1]
        
        last_index = item_split[-1]
        for k in sorted(self.__indexdict.keys()):
            if not k.startswith(parent):
                continue
            #if not
        
    def IsSelected(self, item):
        """ return selected, checked, expanded state of given item """ 
        if isinstance(item, wx._dataview.TreeListItem):            
            return super(TreeListCtrl, self).IsSelected(item)
        
        assert item in self.__indexdict, "not a valid index: %s (%s)" % (str(item), type(item))        
        
        item = self.__indexdict[item]        
        return self.IsSelected(item)
    
    def IsExpanded(self, item):
        """ return selected, checked, expanded state of given item """ 
        if isinstance(item, wx._dataview.TreeListItem):            
            return super(TreeListCtrl, self).IsExpanded(item)
        
        assert item in self.__indexdict, "not a valid index: %s (%s)" % (str(item), type(item))        
        
        item = self.__indexdict[item]        
        return self.IsExpanded(item)
    
    def AppendItem(self, parent, value):
        assert parent in self.__indexdict, "not a valid index: %s (%s)" % (str(parent), type(parent))
          
        item_par = self.__indexdict[parent]
        item = super(TreeListCtrl, self).AppendItem(item_par, value)
        i = 0
        index_chk = parent + ",%d" % i
        while index_chk in self.__indexdict:
            i += 1
            index_chk = parent + ",%d" % i
            
        index = index_chk
        super(TreeListCtrl, self).SetItemData(item, index)
        self.__indexdict[index] = item
        
        return index
        
    def Select(self, index):
        item = self.__indexdict[index]
        super(TreeListCtrl, self).Select(item)
        return index
    
    def AppendItemToRoot(self, value):
        item = super(TreeListCtrl, self).AppendItem(self.__root, value)
        print(self.__toplevelcount)
        print(self.__indexdict)
        index = str(self.__toplevelcount)
        self.SetItemIndex(item, index)
        self.__toplevelcount += 1
        
        self.__indexdict[index] = item
        
        return index
        
    def SetItemIndex(self, item, index):
        super(TreeListCtrl, self).SetItemData(item, index)
    
    def GetItemData(self, *args, **kwargs):
        """ we override this because we want to use data for storing index """
        pass
        
    def SetItemData(self, *args, **kwargs):
        """ we override this because we want to use data for storing index """
        pass
        
    def GetItemDepth(self, item):
        """  backwards """
        depth = 0
        while self.GetItemParent(item).IsOk():
            depth += 1 
            item = self.GetItemParent(item)
        return depth - 1
        
    def GetItemIndex(self, item):
        """ hacky way of getting the item index """
        
        if not item.IsOk():        
            return -1
            
        i = self.GetFirstItem()
        column_count = self.GetColumnCount()
        row = 0
        depth = 0      
        idx = "0"
        root = self.GetItemParent(i)
        while i.IsOk():
            
            d = self.GetItemDepth(i)
            
            # the very first item (not root)
            if d == 0 and row == 0:
                idx = "0"
                row += 1
                
            # a toplevel item (excluding first item)
            elif d == 0 and row > 0:  
                idx = str(row)
                row += 1
                
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
            
            depth = d   # change last depth to current depth
            
            # compare item
            # itmcmp = self.Compare(0, item, i)
            itmcmp = item is i
            print( item == i)
            # if self.
            i = self.GetNextItem(i)
        print( item == i)
        return idx
        
    def GetSubTree(self, item):
        """ return the sub tree of schedule item """
        
        # we stop when item depth is the same as the selected item
        # i.e. a sibling
        selected_depth = self.GetItemDepth(item)                
            
        data = {}
        count = tree.GetColumnCount()       
        depth = selected_depth 
        index = "0"
        
        while item.IsOk():
                        
            d = self.GetItemDepth(item)
            
            # have we reached sibling
            if selected_depth == d and "0" in data:
                break
            
            # selected item is first item
            if d == selected_depth:             
                pass
                
            # sibling of previous item   
            elif d == depth:             
                next = int(index[-1]) + 1
                del index[-1]
                index.append(str(next))
                index = ",".join(index)
                
            # a child of previous item    
            elif d > depth:
                index += ",0"                
                
            # sibling of parent  
            elif d < depth:
                index = index.split(",")[:depth]
                # increment last element
                next = int(index[-1]) + 1
                del index[-1]
                index.append(str(next))
                index = ",".join(index)
            
            # print(index)
            depth = d  
            item_data = {}
            item_data["data"] = tree.GetItemText(item, 0)
            item_data["checked"] = tree.GetCheckedState(item)
            item_data["expanded"] = tree.IsExpanded(item)
            item_data["selected"] = tree.IsSelected(item)
            
            data[index] = item_data
            
            item = tree.GetNextItem(item)
            
        return data
    
    def GetTree(self):
        data = {}
        item = self.GetFirstItem()
        if not item.IsOk():        
            return data
            
        column_count = self.GetColumnCount()
        row = 0
        depth = 0      
        idx = "0"
        data["order"] = [] 
        root = self.GetItemParent(item)
        while item.IsOk():
            d = self.GetItemDepth(item)
            
            # the very first item (not root)
            if d == 0 and row == 0:
                idx = "0"
                row += 1
                
            # a toplevel item (excluding first item)
            elif d == 0 and row > 0:  
                idx = str(row)
                row += 1
                
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
            
            depth = d   # change last depth to current depth
            item_data = {}
            item_data["columns"] = {str(c): self.GetItemText(item, c) for c in range(column_count)}
            item_data["checked"] = self.GetCheckedState(item)
            item_data["expanded"] = self.IsExpanded(item)
            item_data["selected"] = self.IsSelected(item)
            
            data[idx] = item_data
            data["order"].append(idx)
            
            item = self.GetNextItem(item)
        
        return data
        
    def SetTree(self, tree):
        """ set the treelist """  
        self.DeleteAllItems()
        self.__indexdict = {}
        self.__toplevelcount = 0        
        
        if not tree:
            return
            
        items = {}  
        expanded_items = []    
        
        # 
        for idx in sorted(tree.keys()):            
            parent = idx.split(",")[:-1]
            parent = ",".join(parent)
            columns = tree[idx]["columns"]      
            
            if not parent:
                item = self.AppendItemToRoot(columns["0"])
            else:
                parent = items[parent]
                item = self.AppendItem(parent, columns["0"])
                  
            for c in range(1, len(columns)):
                try:
                    self.SetItemText(item, str(c), columns[c])
                except:
                    pass

            checked = tree[idx]["checked"]
            if checked == 1:
                self.CheckItem(item)
            else:
                self.UncheckItem(item)
            selected = tree[idx]["selected"]
            if selected is True:
                self.Select(item)
            expanded = tree[idx]["expanded"] 
            if expanded is True:
                expanded_items.append(item) 
            items[idx] = item
        
        for item in expanded_items:
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
    
    def DeselectAll(self):
        first = self.GetFirstSelected()
        if first == -1:
            return
            
        self.Select(first, on=0)
        item = first
        while self.GetNextSelected(item) != -1:
            item = self.GetNextSelected(item)
            self.Select(self.GetNextSelected(item), on=0)
        
class ConfirmDialog(wx.Dialog):
    
    def __init__(self, parent, title="", caption=""):
        
        wx.Dialog.__init__(self,
                           parent,
                           style=wx.DEFAULT_DIALOG_STYLE)
        
        self.SetTitle(title)
        
        # panel = wx.Panel(self)        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        caption = wx.StaticText(self, label=caption)
        hsizer.Add(caption, 0, wx.ALL|wx.EXPAND)
        
        hsizer2 = wx.BoxSizer(wx.HORIZONTAL)
        # hsizer2.AddStretchSpacer(0)
        for label, id in [("No", wx.ID_NO), ("Yes", wx.ID_YES)]:
            btn = wx.Button(self, id=id, label=label)
            btn.Bind(wx.EVT_BUTTON, self.OnButton)
            hsizer2.Add(btn, 0, wx.ALL, 2)
            
        sizer.AddSpacer(20)
        sizer.Add(hsizer, 2, wx.ALIGN_CENTRE, 5)
        # sizer.AddStretchSpacer()
        sizer.Add(wx.StaticLine(self), 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hsizer2, 1, wx.ALL|wx.ALIGN_CENTRE, 5)
        
        self.SetSizer(sizer)
        
        #idx events binding
        # self.Bind(wx.EVT_idx_UP, self.OnidxUp)
    
    def OnidxUp(self, event):
        idxcode = event.GetidxCode()
        
        if idxcode == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_NO)
        elif idxcode == wx.WXK_ENTER:
            self.EndModal(wx.ID_YES)
        event.Skip()
        
    def OnButton(self, event):
        e = event.GetEventObject()
        id = e.GetId()
        self.EndModal(id)

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