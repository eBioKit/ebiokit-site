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

from django.conf.urls import url

from .application_views import ApplicationViewSet
from .job_views import JobViewSet
from .user_views import UserViewSet

from rest_framework import renderers

# --------------------------------------------------------
# URLs FOR SYSTEM STATUS
# --------------------------------------------------------
system_info = ApplicationViewSet.as_view({
    'get': 'system_info'
}, renderer_classes=[renderers.JSONRenderer])

system_version = ApplicationViewSet.as_view({
    'get': 'system_version'
}, renderer_classes=[renderers.JSONRenderer])

system_settings = ApplicationViewSet.as_view({
    'get': 'get_settings',
    'post': 'update_app_settings'
}, renderer_classes=[renderers.JSONRenderer])

# --------------------------------------------------------
# URLs FOR APPLICATIONS MANAGEMENT
# --------------------------------------------------------
available_updates = ApplicationViewSet.as_view({
    'get': 'available_updates'
}, renderer_classes=[renderers.JSONRenderer])

available_applications = ApplicationViewSet.as_view({
    'get': 'available_applications'
}, renderer_classes=[renderers.JSONRenderer])

# version = ApplicationViewSet.as_view({
#     'get': 'get_app_version'
# }, renderer_classes=[renderers.JSONRenderer])

api_get_all_applications = ApplicationViewSet.as_view({
    'get': 'api_get_all_applications',
    'post': 'create'
})
#
# application_list = ApplicationViewSet.as_view({
#     'post': 'create'
# })

application_status = ApplicationViewSet.as_view({
    'get': 'status'
}, renderer_classes=[renderers.JSONRenderer])

application_start = ApplicationViewSet.as_view({
    'get': 'start'
}, renderer_classes=[renderers.JSONRenderer])

application_stop = ApplicationViewSet.as_view({
    'get': 'stop'
}, renderer_classes=[renderers.JSONRenderer])

application_restart = ApplicationViewSet.as_view({
    'get': 'restart'
}, renderer_classes=[renderers.JSONRenderer])

application_enable = ApplicationViewSet.as_view({
    'get': 'enable'
}, renderer_classes=[renderers.JSONRenderer])

application_disable = ApplicationViewSet.as_view({
    'get': 'disable'
}, renderer_classes=[renderers.JSONRenderer])

application_detail = ApplicationViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

# --------------------------------------------------------
# URLs FOR USERS
# --------------------------------------------------------
api_users = UserViewSet.as_view({
    'get': 'get_user',
    'post': 'api_create_user',
    'update': 'update_user',
})

api_sessions = UserViewSet.as_view({
    'get': 'api_validate_session',
    'post': 'api_sign_in',
    'delete': 'api_sign_out',
})

# --------------------------------------------------------
# URLs FOR JOBS
# --------------------------------------------------------
application_prepare_install = JobViewSet.as_view({
    'get': 'prepare_install'
}, renderer_classes=[renderers.JSONRenderer])

application_prepare_upgrade = JobViewSet.as_view({
    'get': 'prepare_upgrade'
}, renderer_classes=[renderers.JSONRenderer])

application_install = JobViewSet.as_view({
    'post': 'install'
}, renderer_classes=[renderers.JSONRenderer])

application_upgrade = JobViewSet.as_view({
    'post': 'upgrade'
}, renderer_classes=[renderers.JSONRenderer])

application_uninstall = JobViewSet.as_view({
    'get': 'uninstall'
}, renderer_classes=[renderers.JSONRenderer])

application_jobs = JobViewSet.as_view({
    'get': 'check_job_status',
    'delete': 'delete_job'
}, renderer_classes=[renderers.JSONRenderer])

application_jobs_log = JobViewSet.as_view({
    'get': 'get_job_log'
}, renderer_classes=[renderers.JSONRenderer])


urlpatterns = [
    # --------------------------------------------------------
    # URLs FOR SYSTEM STATUS
    # --------------------------------------------------------
    url(r'^system/info/$', system_info, name='system-info'),
    url(r'^system/version/$', system_version, name='system-version'),
    url(r'^system/settings/$', system_settings, name='system-settings'),
    # --------------------------------------------------------
    # URLs FOR USERS
    # --------------------------------------------------------
    url(r'^user/$', api_users, name='api_users'),
    url(r'^session/$', api_sessions, name='api_sessions'),
    # url(r'^version/$', version, name='version'),
    # --------------------------------------------------------
    # URLs FOR APPLICATIONS MANAGEMENT
    # --------------------------------------------------------
    url(r'^applications/available-updates/$', available_updates, name='available-updates'),
    url(r'^applications/available-applications/$', available_applications, name='available-applications'),
    url(r'^applications/$', api_get_all_applications, name='application-list'),
    # --------------------------------------------------------
    # URLs FOR APPLICATION INSTANCE MANAGEMENT
    # --------------------------------------------------------
    url(r'^(?P<instance_name>.+)/status/$', application_status, name='application-status'),
    url(r'^(?P<instance_name>.+)/start/$', application_start, name='application-start'),
    url(r'^(?P<instance_name>.+)/stop/$', application_stop, name='application-stop'),
    url(r'^(?P<instance_name>.+)/restart/$', application_restart, name='application-restart'),
    url(r'^(?P<instance_name>.+)/enable/$', application_enable, name='application-enable'),
    url(r'^(?P<instance_name>.+)/disable/$', application_disable, name='application-disable'),
    url(r'^(?P<instance_name>.+)/$', application_detail, name='application-detail'),
    # --------------------------------------------------------
    # URLs FOR JOBS
    # --------------------------------------------------------
    url(r'^(?P<instance_name>.+)/prepare-install/$', application_prepare_install, name='application-prepare-install'),
    url(r'^(?P<instance_name>.+)/prepare-upgrade/$', application_prepare_upgrade, name='application-prepare-upgrade'),
    url(r'^(?P<instance_name>.+)/install/$', application_install, name='application-install'),
    url(r'^(?P<instance_name>.+)/upgrade/$', application_upgrade, name='application-upgrade'),
    url(r'^(?P<instance_name>.+)/uninstall/$', application_uninstall, name='application-uninstall'),
    url(r'^jobs/(?P<id>.*)$', application_jobs, name='application-jobs'),
    url(r'^task/log/(?P<id>.*)/$', application_jobs_log, name='application-jobs-log')
]
