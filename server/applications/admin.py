"""
(C) Copyright 2021 SLU Global Bioinformatics Centre, SLU
(http://sgbc.slu.se) and the eBioKit Project (http://ebiokit.eu).

This file is part of The eBioKit portal 2021. All rights reserved.
The eBioKit portal is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Lesser General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with eBioKit portal.  If not, see <http://www.gnu.org/licenses/>.

Contributors:
    Dr. Erik Bongcam-Rudloff
    Dr. Rafael Hernandez de Diego (main developer)
    and others.

 More info http://ebiokit.eu/
 Technical contact ebiokit@gmail.com
"""

import importlib, inspect

from django.contrib import admin

from .models import *

for name, cls in inspect.getmembers(importlib.import_module("applications.models"), inspect.isclass):
    if cls.__module__ == 'applications.models':
        AdminClass = type(name + "Admin", (admin.ModelAdmin,), {
            "list_display": cls.get_admin_list_fields()
        })
        admin.site.register(cls, AdminClass)

admin.site.site_header = "eBioKit admin site"
