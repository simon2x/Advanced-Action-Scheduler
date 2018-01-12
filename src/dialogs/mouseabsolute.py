import logging
import platform
import sys
import wx
import wx.lib.agw.floatspin as floatspin
from ast import literal_eval as make_tuple

PLATFORM = platform.system()
if PLATFORM == "Windows":
    from windowmanager import windows as winman
elif PLATFORM == "Linux":
    from windowmanager import linux as winman
    
class FindPosition(wx.Dialog):

    def __init__(self, parent, rect):

        wx.Dialog.__init__(self,
                           parent=None,
                           style=~wx.CAPTION)

        # window rect for determining in/out of bound area
        self._rect = rect
        # self.SetSize((25, 25))
        panel = wx.Panel(self)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._position = wx.StaticText(panel, label="(0,0)")
        sizer.Add(self._position, 0, wx.ALL)

        panel.SetSizer(sizer)

        self._position.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)

        panel.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        panel.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        panel.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        # panel.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)

        self.SetMinSize((90, 60))
        self.SetSize((90, 60))

        # this is important, otherwise the captionless dialog is always maximised
        self.SetMaxSize((90, 60))

        self.Move(wx.GetMousePosition()-(45, 30))

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.timer.Start(1)

    # def OnKillFocus(self, event):
        # self.Destroy()

    def GetValue(self):
        print(self._absolute_position)
        return self._absolute_position
    
    def OnLeftUp(self, event):
        x, y = wx.GetMousePosition()
        self._absolute_position = (x,y)
        self.Close()
    
    def OnKeyUp(self, event):
        key = event.GetKeyCode()
        if key == wx.WXK_ESCAPE:
            self.Close()
        if key == wx.WXK_RETURN:
            self.Close()

    def OnRightUp(self, event):
        self.Destroy()
        
    def OnTimer(self, event):
        self.Raise()
        x, y = wx.GetMousePosition()
        self.Move(wx.GetMousePosition()-(45, 30))

        text = "%d, %d" % (x, y)
        self._position.SetLabel(text)

class MouseClickAbsolute(wx.Dialog):

    def __init__(self, parent):

        wx.Dialog.__init__(self,
                           parent,
                           title="Mouse Click Absolute")

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        sbox = wx.StaticBox(panel, label="")
        sboxSizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        grid = wx.GridBagSizer(5,5)

        row = 0

        lblFunction = wx.StaticText(panel, label="Window:")
        choices = []
        choices.extend(winman.GetWindowList())
        self.cboxWindow = wx.ComboBox(panel, choices=choices)
        btnRefresh = wx.Button(panel, label="Refresh")
        btnRefresh.Bind(wx.EVT_BUTTON, self.OnButton)

        grid.Add(lblFunction, pos=(row,0), flag=wx.ALL|wx.EXPAND|wx.ALIGN_BOTTOM, border=5)
        grid.Add(self.cboxWindow, pos=(row,1), span=(0,2), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(btnRefresh, pos=(row,3), flag=wx.ALL|wx.EXPAND)

        row += 1
        self.chkMatchCase = wx.CheckBox(panel, label="Match Case")
        self.chkMatchCase.SetValue(True)
        self.chk_resize = wx.CheckBox(panel, label="Resize Window")
        self.chk_resize.SetValue(True)
        grid.Add(self.chkMatchCase, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.chk_resize, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)

        row += 1
        lblOffsetX = wx.StaticText(panel, label="Offset (x):")
        self.spinOffsetX = wx.SpinCtrl(panel, min=-10000, max=10000)
        grid.Add(lblOffsetX, pos=(row,1), flag=wx.ALL|wx.EXPAND|wx.ALIGN_BOTTOM, border=5)
        grid.Add(self.spinOffsetX, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)

        row += 1
        lblOffsetY = wx.StaticText(panel, label="Offset (y):")
        self.spinOffsetY = wx.SpinCtrl(panel, min=-10000, max=10000)
        grid.Add(lblOffsetY, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.spinOffsetY, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)

        row += 1
        lblOffsetX = wx.StaticText(panel, label="Width (w):")
        self.spinW = wx.SpinCtrl(panel, min=0, max=10000)
        grid.Add(lblOffsetX, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.spinW, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)
        
        row += 1
        lblOffsetY = wx.StaticText(panel, label="Height (h):")
        self.spinH = wx.SpinCtrl(panel, min=0, max=10000)
        grid.Add(lblOffsetY, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.spinH, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)

        row += 1
        lblX = wx.StaticText(panel, label="x:")
        self.spinX = floatspin.FloatSpin(panel, min_val=0)
        self.spinX.SetDigits(0)
        grid.Add(lblX, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.spinX, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)

        row += 1
        lblY = wx.StaticText(panel, label="y:")
        self.spinY = floatspin.FloatSpin(panel, min_val=0)
        self.spinY.SetDigits(0)
        grid.Add(lblY, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.spinY, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)

        grid.AddGrowableCol(1)
        
        hsizerBtns = wx.BoxSizer(wx.HORIZONTAL)
        for label in ["Reset",
                      "Get Window Pos",
                      "Get Window Size",
                      "Get Window Rect",
                      "Find Position"]:
            btn = wx.Button(panel, label=label)
            btn.Bind(wx.EVT_BUTTON, self.OnButton)
            hsizerBtns.Add(btn, 1, wx.ALL|wx.EXPAND, 5)
                
        sboxSizer.AddSpacer(10)
        sboxSizer.Add(grid, 1, wx.ALL|wx.EXPAND, 5)
        sboxSizer.Add(hsizerBtns, 0, wx.ALL|wx.EXPAND, 5)
        
        #-----
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddStretchSpacer()
        btnCancel = wx.Button(panel, label="Cancel", id=wx.ID_CANCEL)
        btnCancel.Bind(wx.EVT_BUTTON, self.OnButton)
        self.btnAdd = wx.Button(panel, label="Ok", id=wx.ID_OK)
        self.btnAdd.Bind(wx.EVT_BUTTON, self.OnButton)
        
        hsizer.Add(btnCancel, 0, wx.ALL|wx.EXPAND, 5)
        hsizer.Add(self.btnAdd, 0, wx.ALL|wx.EXPAND, 5)

        #add to main sizer
        sizer.Add(sboxSizer, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(hsizer, 0, wx.ALL|wx.EXPAND, 5)

        panel.SetSizer(sizer)
        sizer.Fit(self)

    def GetValue(self):
        data = []
        data.append(("window", self.cboxWindow.GetValue()))
        data.append(("matchcase", self.chkMatchCase.GetValue()))
        data.append(("resize", self.chk_resize.GetValue()))

        data.append(("offsetx", self.spinOffsetX.GetValue()))
        data.append(("offsety", self.spinOffsetY.GetValue()))
        data.append(("width", self.spinW.GetValue()))
        data.append(("height", self.spinH.GetValue()))
        data.append(("x", self.spinX.GetValue()))
        data.append(("y", self.spinY.GetValue()))

        return str(data)
        
    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        id = e.GetId()

        if label == "Get Window Size":
            title = self.cboxWindow.GetValue()

            try:
                offw, offh, w, h = winman.GetWindowRect(title)
            except TypeError as e:
                logging.info(e)
                return

            self.spinOffsetX.SetValue(offw)
            self.spinOffsetY.SetValue(offh)
            self.spinW.SetValue(w)
            self.spinH.SetValue(h)

            self.Raise()

        elif label == "Set Window Size":
            title, win_class = make_tuple(self.cboxWindow.GetValue())

            offw = self.spinOffsetX.GetValue()
            offh = self.spinOffsetY.GetValue()
            w = self.spinW.GetValue()
            h = self.spinH.GetValue()
            winman.SetWindowSize(title, win_class, offw, offh, w, h)

            self.Raise()

        elif label == "Find Position":
            title, win_class = make_tuple(self.cboxWindow.GetValue())
            offw = self.spinOffsetX.GetValue()
            offh = self.spinOffsetY.GetValue()
            w = self.spinW.GetValue()
            h = self.spinH.GetValue()

            # resize the target window
            # windowmanager.SetWindowSize(title, win_class, offw, offh, w, h)

            rect = [offw, offh, w, h]
            finder = FindPosition(self, rect)
            def on_finder_close(event):
                x, y = finder.GetValue()
                logging.info("Got absolute position: %s" % str((x,y)))
                self.spinX.SetValue(int(x))
                self.spinY.SetValue(int(y))
                event.Skip()
                finder.Destroy()
                self.SetFocus()

            finder.Bind(wx.EVT_CLOSE, on_finder_close)

            # finder.SetSize((w,h))
            # finder.SetPosition((offw,offh))
            x, y = self.spinX.GetValue(), self.spinY.GetValue()
            # finder.SetValue((x,y))
            finder.ShowModal()
            finder.SetFocus()

        elif label == "Cancel":
            self.EndModal(id)

        elif label == "Ok":
            self.EndModal(id)

        elif label == "Refresh":
            value = self.cboxWindow.GetValue()
            self.cboxWindow.Clear()
            choices = []
            choices.extend(winman.GetWindowList())
            self.cboxWindow.Append(choices)
            self.cboxWindow.SetValue(value)

    def SetValue(self, data):
        window = data["window"]
        self.cboxWindow.SetValue(window)

        case = data["matchcase"]
        resize = data["resize"]
        self.chkMatchCase.SetValue(case)
        self.chk_resize.SetValue(resize)

        offsetx = data["offsetx"]
        offsety = data["offsety"]
        self.spinOffsetX.SetValue(offsetx)
        self.spinOffsetY.SetValue(offsety)

        width = data["width"]
        height = data["height"]
        self.spinW.SetValue(width)
        self.spinH.SetValue(height)

        x = data["x"]
        y = data["y"]
        self.spinX.SetValue(x)
        self.spinY.SetValue(y)
        
#        