import wx
import wx.dataview
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin, CheckListCtrlMixin

class TreeListCtrl(wx.dataview.TreeListCtrl):
    
    def __init__(self, parent):
        """
        Tree data format
        
        index = "n,n,n, ..."    
        ...where the first n is a top-level parent. Subsequent n
        are children of the left n
        
        """
        
        style = wx.dataview.TL_CHECKBOX
        wx.dataview.TreeListCtrl.__init__(self, 
                                          parent,
                                          style=style)
              
    def GetSubTree(self, item):
        """ return the sub tree of schedule item """
        tree = self.sched_list
        
        selection = item
        
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
            
            item = tree.GetNextItem(item)
        
        return data
        
    def SetTree(self, data)
        """ set the treelist """  
        self.DeleteAllItems()
                
        if not data:
            return
                
        items = {}  
        expanded_items = []        
        root = self.GetRootItem()
        for idx in sorted(data.keys()):            
            parent = idx.split(",")[:-1]
            parent = ",".join(parent)
            if not parent:
                parent = root
            else:
                parent = items[parent]
            
            column_count = self.GetColumnCount()
            columns = data[idx]["columns"]
            item = self.AppendItem(parent, value)
            if column_count > 1:
                for c in range(0, column_count):
                    try:
                        self.SetItemText(item, c, columns[c])
                    except:
                        pass
            
            checked = data[idx]["checked"]
            if checked == 1:
                self.CheckItem(item)
            else:
                self.UncheckItem(item)
            selected = data[idx]["selected"]
            if selected is True:
                self.Select(item)
            expanded = data[idx]["expanded"] 
            if expanded is True:
                expanded_items.append(item) 
            items[idx] = item
        
        for item in expanded_items:
            tree.Expand(item)
            
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