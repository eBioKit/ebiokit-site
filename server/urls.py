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

from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import TemplateView

urlpatterns = [
    url(r'^api/', include('applications.urls')),
    url(r'^back/', admin.site.urls), #TODO: REMOVE
    url(r'^$', TemplateView.as_view(template_name="index.html"), name='index'),
    url(r'^home$', TemplateView.as_view(template_name="resources/home.html"), name='home'),
    url(r'^update$', TemplateView.as_view(template_name="resources/update.html"), name='update'),
    url(r'^admin$', TemplateView.as_view(template_name="admin.html"), name='admin')
]
