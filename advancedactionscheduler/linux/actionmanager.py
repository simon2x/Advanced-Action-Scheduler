# -*- coding: utf-8 -*
"""
@author Simon Wu <swprojects@runbox.com>

Copyright (c) 2018 by Simon Wu <Advanced Action Scheduler>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

"""
linuxactionmanager.py

note: when wmctrl retrieves the geometry of a window, it doesn't account
      for the window decorations, which varies across desktop environments

      This complicates the method for getting the window rect. We deal with
      this using the GetDecoratedWindowOffset function

future: remove xdotool dependencs
"""
