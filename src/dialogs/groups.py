
import logging
import sys
import time
import wx
import base

class AddGroup(wx.Dialog):

    def __init__(self, parent):
    
        wx.Dialog.__init__(self,
                           parent,
                           title="Add New Group")
        
        panel = wx.Panel(self) 
        sizer = wx.BoxSizer(wx.VERTICAL)
                
        sbox = wx.StaticBox(panel, label="")        
        sbox_sizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        
        
        
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        lbl_name = wx.StaticText(panel, label="Name:", style=wx.TE_PROCESS_ENTER)
        self.text_name = wx.TextCtrl(panel)
        self.text_name.Bind(wx.EVT_TEXT_ENTER, self.OnFunctionEnter)        
        hsizer.Add(lbl_name, 0, wx.ALL|wx.ALIGN_CENTRE, 5)
        hsizer.Add(self.text_name, 0, wx.ALL|wx.ALIGN_BOTTOM, 5)
        sbox_sizer.Add(hsizer, 0, wx.ALL|wx.EXPAND, 5)
        
        #-----        
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddStretchSpacer()
        btn_cancel = wx.Button(panel, label="Cancel", id=wx.ID_CANCEL)
        btn_cancel.Bind(wx.EVT_BUTTON, self.OnButton)
        self.btn_add = wx.Button(panel, label="Add", id=wx.ID_OK)
        self.btn_add.Bind(wx.EVT_BUTTON, self.OnButton)
        hsizer.Add(btn_cancel, 0, wx.ALL|wx.EXPAND, 5)
        hsizer.Add(self.btn_add, 0, wx.ALL|wx.EXPAND, 5)
                        
        #add to main sizer
        sizer.Add(sbox_sizer, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hsizer, 0, wx.ALL|wx.EXPAND, 5)
        
        panel.SetSizer(sizer)  
        
        w, h = sizer.Fit(self)
        
        try:
            self.SetIcon(theme.GetIcon("psu_png"))
        except:
            pass
    
    def OnFunctionEnter(self, event):
        self.EndModal(wx.ID_OK)
    
    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        id = e.GetId()
        
        if label == "Cancel":
            self.EndModal(id)            
        elif label == "Add":     
            if self.text_name.GetValue() != "":
                self.EndModal(id)
    
    def SetValue(self, value): 
        self.text_name.SetValue(value)
        
    def GetValue(self): 
        name = self.text_name.GetValue()          
        return name