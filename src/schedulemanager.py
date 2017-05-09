"""
Copyright (c) <year> <copyright holders>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import base
import windowmanager
import logging
import pyautogui
import time
import webbrowser

from ast import literal_eval as make_tuple
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler

DELIMITER = " ➡ "

class Manager:
    
    def __init__(self, parent):
        
        self._parent = parent
        self._schedules = {}
        self._sched_data = {}
        
        # populate with group names
        self._group_names = {}
    
    def GetParent(self):
        return self._parent
    
    def AddSchedules(self, group_data):
        """ this method is processing the group's schedules """
        
        group = group_data["name"]
        schedules = group_data["schedules"]
        group_checked = group_data["checked"]
                
        _schedules = {group: {}}
        for idx, v in schedules.items():           
                        
            # is a schedule?
            if "," not in idx:       
                d = v["data"]["0"]
                sched_name, sched_time = d.split(DELIMITER)
                
                sched_time = make_tuple(sched_time)
                sched_time = {k:v for k,v in sched_time}            
                
                params = {}
                for timevar in ["dof","h","m","s"]:
                    if timevar in sched_time:
                        params[timevar] = ",".join([t for t in sched_time[timevar]])
                    else:
                        params[timevar] = "*"            
                
                schedule = BackgroundScheduler()
                crontrig = CronTrigger(day_of_week=params["dof"],
                                       hour=params["h"], 
                                       minute=params["m"],
                                       second=params["s"])
                
                args = (group, idx)
                job = schedule.add_job(self.OnSchedule, args=[args], trigger=crontrig)
                                             
                checked = v["checked"]
                _schedules[group][idx] = (sched_name, checked, schedule)
            
            # ...is an action
            else:
                d = v["data"]["0"]
                action, params = d.split(DELIMITER)
                params = make_tuple(params)
                try:
                    self._sched_data[group][sched_name][idx] = params
                except:
                    self._sched_data[group] = {sched_name: {idx: params}}
              
        # finally, start the checked schedules of the checked groups    
        for group, scheds in _schedules.items():
            self._schedules[group] = scheds
            for i,s in scheds.items():         
                if s[1] == 0:
                    continue 
                    
                s[2].start()
                self.SendLog(["-","Started schedule %s from %s group" % (s[0], group)])
            
    def SetSchedules(self, data):
        """ process schedule data """
        
        # stop and remove schedules first
        self.Stop()
        
        for idx, group_data in data.items():          
            self.AddSchedules(group_data)            

    def DoAction(self, action, kwargs):
        logging.info("Executing action: %s" % action)
        logging.info("parameters: %s" % str(kwargs))
        
        #convert tuple list to dictionary
        kwargs = {k:v for k,v in kwargs}
        
        if action == "CloseWindow":
            window = kwargs["window"]
            matchcase = kwargs["matchcase"]
            matchstring = kwargs["matchstring"]
            
            windowmanager.CloseWindow(window, matchcase, matchstring)
            
        elif action == "Delay":
            delay = kwargs["delay"]
            delay = int(delay.pop("s"))
            time.sleep(delay)
            
        elif action == "KillProcess":
            pass
            
        elif action == "IfWindowOpen":
            window = kwargs["window"]
            matchcase = kwargs["matchcase"]
            matchstring = kwargs["matchstring"]
            
            if not windowmanager.FindWindow(window, matchcase):
                # no window found
                return False
            
            return True 
            
        elif action == "IfWindowNotOpen":
            window = kwargs["window"]
            matchcase = kwargs["matchcase"]
            matchstring = kwargs["matchstring"]
            
            if windowmanager.FindWindow(window, matchcase):
                # window found
                return False
            
            return True 
            
        elif action == "MouseClickAbsolute":
            title, win_class = make_tuple(kwargs["window"])
            matchcase = kwargs["matchcase"]
            resize = kwargs["resize"]
            offsetx = kwargs["offsetx"]
            offsety = kwargs["offsety"]
            width = kwargs["width"]
            height = kwargs["height"]
            x = kwargs["x"]
            y = kwargs["y"]
           
            windowmanager.SetWindowSize(title, win_class, offsetx, offsety, width, height)
            pyautogui.click(x=x, y=y)
            
            
        elif action == "MouseClickRelative":
            window = kwargs["window"]
            matchcase = kwargs["matchcase"]
            resize = kwargs["resize"]
            offsetx = kwargs["offsetx"]
            offsety = kwargs["offsety"]
            width = kwargs["width"]
            height = kwargs["height"]
            x = kwargs["x"]
            y = kwargs["y"]
            
        elif action == "OpenURL":
            url = kwargs["url"]
            browser = kwargs["browser"]
            newwindow = kwargs["newwindow"]
            autoraise = kwargs["autoraise"]
            print (webbrowser._browsers)
            return
            if browser != "system default":
                b = webbrowser.get(browser)
            else:
                b = webbrowser.get(browser)
            
            if newwindow and autoraise:
                b.open(newwindow, new=1, sautoraise=True)
            elif newwindow and not autoraise:
                b.open(newwindow, new=1, autoraise=False)
            elif not newwindow and autoraise:
                b.open(newwindow, new=0, autoraise=True)
            elif not newwindow and not autoraise:
                b.open(newwindow, new=0, autoraise=False)
            
        elif action == "Power":
            action = kwargs["action"]
            alert = kwargs["alert"]
            
        elif action == "StopSchedule":
            schedule = kwargs["schedule"]
            
        elif action == "StartSchedule":
            schedule = kwargs["schedule"]
            
        elif action == "SwitchWindow":
            window = kwargs["window"]
            matchcase = kwargs["matchcase"]
            matchstring = kwargs["matchstring"]
            
        return True
     
    def OnSchedule(self, args):
        group, index = args
        
        print(self._sched_data)
        return
        name = self._schedules[group][index][0]
        logging.info("On schedule: %s,%s" % (index, name))
        if name not in self._sched_data:
            print("no actions to run")
            return
        
        exit()
        # get item from index, and its immediate
        idx = 0
        item = tree.GetFirstItem()
        while item.IsOk():
        
            # if the schedule is unchecked, set item to next sibling
            checked = tree.GetCheckedState(item)
            if checked == 0:
                item = tree.GetNextSibling(item)
                
            if idx == index:
                break
                
            item = tree.GetNextSibling(item)            
            idx += 1            
                
        # now iterate through items children
        # and invoke the relevant actions
        sched_item = item
        # next item of schedule, if depth is zero we have reached
        # the next sibling and should stop 
        item = tree.GetNextItem(sched_item)
        depth = 1 #first item should always be 1
        while item.IsOk() and depth != 0:
            
            result = True
            checked = tree.GetCheckedState(item)
            if checked == 1:
                item_text = tree.GetItemText(item)
                action, params = item_text.split(DELIMITER)
                params = make_tuple(params)
                result = self.DoAction(action, params)
                
                if result is True:
                    item = tree.GetNextItem(item)
                else:
                    # action failed condition, skip to next sibling
                    item = tree.GetNextSibling(item)
                    
            elif checked == 0:
                # no action required, skip to next sibling
                item = tree.GetNextSibling(item)
            
            if item.IsOk():
                depth = parent.GetItemDepth(item)
            
        
        return
        
        PROCNAME = "python.exe"
        
        for proc in psutil.process_iter():
            if proc.name() == PROCNAME:
                print(proc)        

    def SendLog(self, message):
        """ pass message to schedule manager lis """
        parent = self.GetParent()
        parent.AppendLogMessage(message)
        
    def Stop(self):
        """ shutdown all schedules """
        print(self._schedules)
        
        for group, data in self._schedules.items():            
            for idx, schedules in data.items():
                if schedules[1] == 0:
                    continue
                s = schedules[2]
                s.shutdown()
                
                name = schedules[0]                
                self.SendLog(["-",
                              "Stopped schedule %s from group %s" % (name, group)])
        
        self.SendLog(["-","All schedules have been stopped"])
        
        # clear schedules
        self._schedules = {}
        
    def Start(self):
        pass    

# placeholder comment. For some reason, notepad++ doesn't detect function  
# list correctly without this