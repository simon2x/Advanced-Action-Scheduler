import wx
import base

class AddDelay(wx.Dialog):

    def __init__(self, parent):

        wx.Dialog.__init__(self,
                           parent,
                           title="Add Delay")

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        sbox = wx.StaticBox(panel, label="")
        sboxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        grid = wx.GridBagSizer(5,5)

        row = 0
        self.spinDelay = wx.SpinCtrl(panel, max=99, min=0)
        self.spinDelay2 = wx.SpinCtrl(panel, max=99, min=0)
        self.spinDelay.Bind(wx.EVT_SPINCTRL, self.OnSpinDelay)
        self.spinDelay2.Bind(wx.EVT_SPINCTRL, self.OnSpinDelay)
        self.labelDelayValue = wx.StaticText(panel, label="0.0s")
        grid.Add(self.spinDelay, pos=(row,1), span=(2,2), flag=wx.ALL|wx.ALIGN_BOTTOM, border=5)
        grid.Add(self.spinDelay2, pos=(row,3), span=(2,2), flag=wx.ALL|wx.ALIGN_BOTTOM, border=5)
        grid.Add(self.labelDelayValue, pos=(row,5), span=(2,2), flag=wx.ALL|wx.ALIGN_CENTRE, border=5)

        sboxSizer.Add(grid, 1, wx.ALL|wx.EXPAND, 10)
        sboxSizer.AddSpacer(10)

        #-----
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddStretchSpacer()
        btnCancel = wx.Button(panel, label="Cancel", id=wx.ID_CANCEL)
        btnCancel.Bind(wx.EVT_BUTTON, self.OnButton)
        btnConfirm = wx.Button(panel, label="Confirm", id=wx.ID_OK)
        btnConfirm.Bind(wx.EVT_BUTTON, self.OnButton)
        hsizer.Add(btnCancel, 0, wx.ALL|wx.EXPAND, 5)
        hsizer.Add(btnConfirm, 0, wx.ALL|wx.EXPAND, 5)

        #add to main sizer
        sizer.Add(sboxSizer, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(hsizer, 0, wx.ALL|wx.EXPAND, 5)

        panel.SetSizer(sizer)
        w, h = sizer.Fit(self)

        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)

    def GetValue(self):
        data = [("delay",str(self.labelDelayValue.GetLabel()))]
        data = str(data)
        return data
        
    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        id = e.GetId()

        if label == "Cancel":
            self.EndModal(id)
        elif label == "Confirm":
            self.EndModal(id)
            
    def OnKeyUp(self, event):
        key = event.GetKeyCode()
        print(event)
        if key == wx.KEY_ESCAPE:
            self.EndModal(wx.ID_CANCEL)

    def OnSpinDelay(self, event=None):
        s0 = self.spinDelay.GetValue()
        s1 = self.spinDelay2.GetValue()

        label = str(s0) + "." + str(s1) + "s"
        self.labelDelayValue.SetLabel(label)
        
    def SetValue(self, data):
        delay = data["delay"]

        self.labelDelayValue.SetLabel(delay)

        #increment delay
        spin1, spin2 = delay[:-1].split(".")

        self.spinDelay.SetValue(spin1)
        self.spinDelay2.SetValue(spin2)