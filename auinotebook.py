
import wx
import wx.lib.agw.aui as aui 
#------------------------------------------------#

class Main(wx.Frame):

    def __init__(self):
        
        self._title = "aui notebook example in a splitter"
        
        wx.Frame.__init__(self,
                          parent=None,
                          title=self._title)
         
        self.splitter = wx.SplitterWindow(self)
        
        leftpanel = wx.Panel(self.splitter)   
        leftsizer = wx.BoxSizer(wx.VERTICAL)
        leftpanel.SetBackgroundColour("red")
        
        # rhs layout
        
        nbpanel = wx.Panel(self.splitter)   
        self.notebook = aui.AuiNotebook(nbpanel)
        nbsizer = wx.BoxSizer(wx.VERTICAL)
        nbsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 2)
        
        
        schedpanel = wx.Panel(self.notebook)   
        schedsizer = wx.BoxSizer(wx.VERTICAL)
        schedpanel.SetSizer(schedsizer)        
        
        self.notebook.AddPage(schedpanel, "Schedules")
        nbpanel.SetSizer(nbsizer)
        
        self.splitter.SplitVertically(leftpanel, nbpanel)
        self.splitter.SetSashGravity(0.4)
        
        self.SetMinSize((600, 600))
        self.SetSize((600, 600))
        
        self.Show()
        
if __name__ == "__main__":
    app = wx.App()    
    Main()
    app.MainLoop()
    