#!/usr/bin/python3
# -*- coding: utf-8 -*
"""
@author Simon Wu <swprojects@runbox.com>

Copyright (c) 2018 by Simon Wu <Advanced Action Scheduler>
Released subject to the GNU Public License

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""


DELIMITER = " ➡ "

FUNCTIONKEYS = {
    340: 'F1',
    341: 'F2',
    342: 'F3',
    343: 'F4',
    344: 'F5',
    345: 'F6',
    346: 'F7',
    347: 'F8',
    348: 'F9',
    349: 'F10',
    350: 'F11',
    351: 'F12',
    352: 'F13',
    353: 'F14',
    354: 'F15',
    355: 'F16',
    356: 'F17',
    357: 'F18',
    358: 'F19',
    359: 'F20',
    360: 'F21',
    361: 'F22',
    362: 'F23',
    363: 'F24'
}

RESERVEDHOTKEYS = [
    "CTRL+E",
    "CTRL+I",
    "CTRL+N",
    "CTRL+O",
    "CTRL+S",
    "CTRL+SHIFT+S",
    "CTRL+W",
    "CTRL+T",
    "CTRL+V",
    "CTRL+C",
    "CTRL+X",
    "CTRL+A"
]

FUNCTIONS = [
    "CloseWindow",
    "Control",
    "Delay",
    # "KillProcess",
    "IfWindowOpen",
    "IfWindowNotOpen",
    "MouseClickAbsolute",
    "MouseClickRelative",
    "NewProcess",
    "OpenURL",
    "Power",
    "StopSchedule",
    "StartSchedule",
    "SwitchWindow"
]
