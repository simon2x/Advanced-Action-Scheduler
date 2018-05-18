# -*- coding: utf-8 -*
"""
@author Simon Wu <swprojects@runbox.com>

Copyright (c) 2018 by Simon Wu <Advanced Action Scheduler> 

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version. 
"""

# This is intended as a temporary workaround for
# python module 'keyboard' lack of non-root support.
# So currently, we disable global hotkey support instead
# of asking for elevated privileges.
class DummyKeyboard:

    def __init__(self, *args, **kwargs):
        pass
        
    def add_hotkey(self, *args, **kwargs):
        pass
        
    def unhook_all(self, *args, **kwargs):
        pass
        
keyboard = DummyKeyboard()
