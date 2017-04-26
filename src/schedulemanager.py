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
       
    def GetParent(self):
        return self._parent
        
    def Stop(self):
        """ shutdown all schedules """
        for index, schedule in self._schedules.items():            
            name, schedule = schedule
            schedule.shutdown()
            logging.info("Shutdown schedule: %s" % name)
        
        self._schedules = {}
        
    def Start(self):
        pass
                
    def SetSchedules(self, schedules):
        """ process schedule data """
        
        # stop and remove schedules first
        self.Stop()
        
        for index, schedule in enumerate(schedules):            
            sched_name, sched_time = schedule.split(DELIMITER)
            
            sched_time = make_tuple(sched_time)
            sched_time = {k:v for k,v in sched_time}            
            
            params = {}
            for timevar in ["dof","h","m","s"]:
                if timevar in sched_time:
                    params[timevar] = ",".join([t for t in sched_time[timevar]])
                else:
                    params[timevar] = "*"            
            
            _schedule = BackgroundScheduler()
            crontrig = CronTrigger(day_of_week=params["dof"],
                                   hour=params["h"], 
                                   minute=params["m"],
                                   second=params["s"])
            job = _schedule.add_job(self.OnSchedule, args=[index], trigger=crontrig)
                                         
            self._schedules[index] = (sched_name, _schedule)
            _schedule.start()
    
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
         
    def OnSchedule(self, index):
        name = self._schedules[index][0]
        logging.info("On schedule: %s,%s" % (index, name))
        
        parent = self.GetParent()
        tree = parent.GetTree()
        
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