# -*- coding: utf-8 -*
"""
@author Simon Wu <swprojects@runbox.com>

Copyright (c) 2018 by Simon Wu <Advanced Action Scheduler> 

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version. 
"""

import requests
import wx
from wx.lib.agw import hyperlink
from threading import Thread

# ex https://sourceforge.net/projects/advanced-action-scheduler/files/v0.1.1/
baseUrl = "https://sourceforge.net/projects/advanced-action-scheduler/files/"

class UpdateCheckThread(Thread):

    def __init__(self, version, latestVersion):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self.version = version
        self.latestVersion = latestVersion
        
    def run(self):
        currentMajor, currentMinor, currentPatch = self.version
        
        # check for latest major version
        major = currentMajor
        for p in range(currentMajor, 20):
            response = requests.get("{0}v{1}.0.0/".format(baseUrl, p), timeout=2)
            if (response.status_code > 400): # 404 error if non-existant
                break
            major = p # latest
            
        # check for latest minor version of latest major 
        minor = currentMinor
        for m in range(0, 11): # must check from zero
            if major == 0 and m == 0:    
                continue # ignore v0.0.0
            response = requests.get("{0}v{1}.{2}.0/".format(baseUrl, major, m), timeout=2)
            print("{0}v{1}.{2}.0/".format(baseUrl, major, m))
            if (response.status_code > 400): # 404 error if non-existant
                break
            minor = m # latest
        
        # check for latest patch of latest major.minor release 
        patch = currentPatch
        for q in range(0, 20): # must check from zero
            response = requests.get("{0}v{1}.{2}.{3}/".format(baseUrl, major, minor, q), timeout=2)
            print("{0}v{1}.{2}.{3}/".format(baseUrl, major, minor, q))
            if (response.status_code > 400): # 404 error if non-existant
                break 
            patch = q # latest
        
        self.latestVersion.extend([major, minor, patch])      
                
class CheckForUpdates(wx.Dialog):

    def __init__(self, parent, version):
        wx.Dialog.__init__(self, parent, title="Check For Updates")
        
        self.version = version
        self.latestVersion = []
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sbox = wx.StaticBox(panel, label="")
        sboxSizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        
        v = "v" + ".".join([str(s) for s in version])
        versionLabel = wx.StaticText(panel, label="Current Version: %s" % v)
        self.latestVersionLabel = wx.StaticText(panel, label="Latest Version:")
        self.versionStatus = wx.StaticText(panel, label="")
        g = "https://sourceforge.net/projects/advanced-action-scheduler/files/"
        link = hyperlink.HyperLinkCtrl(panel, label="Check Releases Manually", URL=g)
        hSizerLink = wx.BoxSizer(wx.HORIZONTAL)
        self.linkLabel = wx.StaticText(panel)
        self.link = hyperlink.HyperLinkCtrl(panel, label="", URL=g)
        hSizerLink.Add(self.linkLabel, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        hSizerLink.Add(self.link, 0, wx.ALL|wx.EXPAND, 5)
        
        sboxSizer.Add(link, 0, wx.ALL|wx.EXPAND, 5)
        sboxSizer.Add(versionLabel, 0, wx.ALL|wx.EXPAND, 5)
        sboxSizer.Add(self.latestVersionLabel, 0, wx.ALL|wx.EXPAND, 5)
        sboxSizer.Add(self.versionStatus, 0, wx.ALL|wx.EXPAND, 5)
        sboxSizer.Add(hSizerLink, 1, wx.ALL|wx.EXPAND, 5)
        
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btnCancel = wx.Button(panel, label="Cancel", id=wx.ID_CANCEL)
        self.btnCheck = wx.Button(panel, label="Check")
        self.btnCheck.SetFocus()
        # self.btnUpdate = wx.Button(panel, label="Update")
        # self.btnUpdate.Disable()
        self.btnCancel.Bind(wx.EVT_BUTTON, self.OnCancel)
        self.btnCheck.Bind(wx.EVT_BUTTON, self.OnCheck)
        # self.btnUpdate.Bind(wx.EVT_BUTTON, self.OnUpdate)
        
        hSizer.Add(self.btnCancel, 0, wx.ALL|wx.EXPAND, 5)
        hSizer.AddStretchSpacer()
        hSizer.Add(self.btnCheck, 0, wx.ALL|wx.EXPAND, 5)
        # hSizer.Add(self.btnUpdate, 0, wx.ALL|wx.EXPAND, 5)
        
        #add to main sizer
        sizer.Add(sboxSizer, 1, wx.ALL|wx.EXPAND, 5)
        sizer.Add(hSizer, 0, wx.ALL|wx.EXPAND, 5)

        panel.SetSizer(sizer)
        w, h = sizer.Fit(self)
        self.SetMinSize((w*1.5, h))
        self.SetSize((w*1.5, h))
        self.Show()
                
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        
    def OnTimer(self, event=None):
        if self.latestVersion is [] or not self.latestVersion:
            return
            
        print(self.latestVersion)
        v = "v" + ".".join([str(s) for s in self.latestVersion])
        self.latestVersionLabel.SetLabel("Latest Version: %s" % v)
        self.btnCheck.SetLabel("Check")
        if self.version == self.latestVersion:
            self.versionStatus.SetLabel("No Updates Are Available")
            return
            
        self.versionStatus.SetLabel("Updates Are Available")
        self.link.SetLabel("Latest Release: {0}".format(v))
        self.link.SetURL("{0}{1}".format(baseUrl, v))
        self.timer.Stop()
        
    def OnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)
        
    def OnCheck(self, event):
        self.latestVersion = []
        self.versionStatus.SetLabel("")
        self.latestVersionLabel.SetLabel("Latest Version:")
        self.link.SetLabel("")
        self.link.SetURL("")
        thread = UpdateCheckThread(self.version, self.latestVersion)
        thread.daemon = True
        thread.start()
        self.timer.Start(500)
        self.btnCheck.SetLabel("Checking...")