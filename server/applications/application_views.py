"""
(C) Copyright 2017 SLU Global Bioinformatics Centre, SLU
(http://sgbc.slu.se) and the eBioKit Project (http://ebiokit.eu).

This file is part of The eBioKit portal 2017. All rights reserved.
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

from rest_framework import viewsets
from models import Application, RemoteServer, Settings, User
from serializers import ApplicationSerializer
from django.http import JsonResponse
from rest_framework.decorators import detail_route
from rest_framework import renderers
from os import path as osPath
from resources.UserSessionManager import UserSessionManager
from django.conf import settings

import psutil
import subprocess
import requests


class ApplicationViewSet(viewsets.ModelViewSet):
    """ ViewSet for viewing and editing Application objects """
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    lookup_field = "instance_name"

    #---------------------------------------------------------------
    #- RETRIEVE INFORMATION
    #---------------------------------------------------------------
    @detail_route(renderer_classes=[renderers.JSONRenderer])
    def system_info(self, request, name=None):
        # UserSessionManager().validate_admin_session(request.COOKIES.get("ebiokitsession"))
        return JsonResponse({
            'cpu_count' : psutil.cpu_count(),
            "cpu_use" : psutil.cpu_percent(),
            "mem_total" : psutil.virtual_memory().total/(1024.0**3),
            "mem_use" : psutil.virtual_memory().percent,
            "swap_total": psutil.swap_memory().total/(1024.0**3),
            "swap_use" : psutil.swap_memory().percent
        })

    @detail_route(renderer_classes=[renderers.JSONRenderer])
    def ebiokit_machine_status(self, request):
        UserSessionManager().validate_admin_session(request.COOKIES.get("ebiokitsession"))
        settings = self.read_settings(request)
        command = "status"
        command = osPath.join(osPath.dirname(osPath.realpath(__file__)), '../admin_tools/ebiokit_launcher.sh') + ' "' + settings.get("ebiokit_host") + '" "' + settings.get("ebiokit_password") + '" "' + settings.get("platform") + '" "' + command + '"'
        output = subprocess.check_output(['bash', '-c', command])
        return JsonResponse({'ebiokit_machine_status': output.rstrip()})

    @detail_route(renderer_classes=[renderers.JSONRenderer])
    def ebiokit_machine_start(self, request):
        UserSessionManager().validate_admin_session(request.COOKIES.get("ebiokitsession"))
        settings = self.read_settings(request)
        command = "startup"
        command = osPath.join(osPath.dirname(osPath.realpath(__file__)), '../admin_tools/ebiokit_launcher.sh') + ' "' + settings.get("ebiokit_host") + '" "' + settings.get("ebiokit_password") + '" "' + settings.get("platform") + '" "' + command + '"'
        output = subprocess.check_output(['bash', '-c', command])
        return JsonResponse({'success': "true"})

    @detail_route(renderer_classes=[renderers.JSONRenderer])
    def available_updates(self, request, name=None):
        UserSessionManager().validate_admin_session(request.COOKIES.get("ebiokitsession"))

        #Step 1. Get all services from remote server
        mainRemoteServer = RemoteServer.objects.get(enabled=1)
        r = requests.get(mainRemoteServer.url.rstrip("/") + "/api/available-applications")
        if r.status_code != 200:
            return JsonResponse({'success': False, 'error_message' : 'Unable to retrieve available services from ' + mainRemoteServer.name})

        installedApps = Application.objects.all()
        currentVersions = {}
        for application in installedApps.iterator():
            currentVersions[application.instance_name] = application.version

        responseContent = []
        availableApps = r.json().get("availableApps")
        for application in availableApps:
            if currentVersions.has_key(application.get("name")) and currentVersions.get(application.get("name")) != application.get("version"):
                responseContent.append({'name' : application.get("name"), 'current_version' : currentVersions.get(application.get("name")), "new_version" : application.get("version")})

        return JsonResponse({'available_updates': responseContent })

    @detail_route(renderer_classes=[renderers.JSONRenderer])
    def available_applications(self, request, name=None):
        UserSessionManager().validate_admin_session(request.COOKIES.get("ebiokitsession"))

        #Step 1. Get all services from remote server
        mainRemoteServer = RemoteServer.objects.get(enabled=1)
        r = requests.get(mainRemoteServer.url.rstrip("/") + "/api/available-applications")
        if r.status_code != 200:
            return JsonResponse({'success': False, 'error_message' : 'Unable to retrieve available services from ' + mainRemoteServer.name})
        return JsonResponse({'repository_name': mainRemoteServer.name, 'repository_url': mainRemoteServer.url, 'availableApps': r.json().get("availableApps")})

    @detail_route(renderer_classes=[renderers.JSONRenderer])
    def system_version(self, request, name=None):
        APP_VERSION = getattr(settings, "APP_VERSION", 0)
        try:
            UserSessionManager().validate_admin_session(request.COOKIES.get("ebiokitsession"))
            #Step 1. Get the latest version
            mainRemoteServer = RemoteServer.objects.get(enabled=1)
            r = requests.get(mainRemoteServer.url.rstrip("/") + "/api/latest-version")
            if r.status_code != 200:
                return JsonResponse({'success': False, 'error_message' : 'Unable to retrieve the latest version from ' + mainRemoteServer.name})
            return JsonResponse({'system_version': APP_VERSION, 'latest_version': r.json().get("latest_version")})
        except:
            return JsonResponse({'system_version': APP_VERSION})

    @detail_route(renderer_classes=[renderers.JSONRenderer])
    def get_settings(self, request):
        UserSessionManager().validate_admin_session(request.COOKIES.get("ebiokitsession"))
        return JsonResponse({'settings': self.read_settings(request)})

    @detail_route(renderer_classes=[renderers.JSONRenderer])
    def update_app_settings(self, request):
        user_id = UserSessionManager().validate_admin_session(request.COOKIES.get("ebiokitsession"))

        settings = request.data.get("settings", {})
        if settings.has_key("password") and settings["password"] != "" and settings["password"] == settings["password2"]:
            try:
                user = User.objects.get(email=user_id, password=settings.get("prev_password", ""))
                user.password = settings["password"]
                user.save()
            except:
                response = JsonResponse({'success': False, 'err_code': 404001})
                response.status_code = 500
                return response

        self.update_settings(request)
        return JsonResponse({'success': True})

    #---------------------------------------------------------------
    #- ADMINISTRATE SERVICES
    #---------------------------------------------------------------
    @detail_route(renderer_classes=[renderers.JSONRenderer])
    def status(self, request, instance_name=None):
        UserSessionManager().validate_admin_session(request.COOKIES.get("ebiokitsession"))

        service_instance = Application.objects.filter(instance_name=instance_name)[:1]
        if (len(service_instance) == 0):
            return JsonResponse({'success': False, 'error_message': 'Service instance cannot be found'})

        p = subprocess.Popen(osPath.join(osPath.dirname(osPath.realpath(__file__)), '../admin_tools/service') + " " + instance_name + " status --no-cmd", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()

        return JsonResponse({'status': output.replace("\n",""), 'status_msg' : err})

    @detail_route(renderer_classes=[renderers.JSONRenderer])
    def start(self, request, instance_name=None):
        UserSessionManager().validate_admin_session(request.COOKIES.get("ebiokitsession"))

        service_instance = Application.objects.filter(instance_name=instance_name)[:1]
        if (len(service_instance) == 0):
            return JsonResponse({'success': False, 'error_message': 'Service instance cannot be found'})

        p = subprocess.Popen(osPath.join(osPath.dirname(osPath.realpath(__file__)), '../admin_tools/service') + " " + instance_name + " start", stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        returncode = p.returncode
        success = (returncode == 0)
        return JsonResponse({'success': success, "stdout": output, 'stderr': err})

    @detail_route(renderer_classes=[renderers.JSONRenderer])
    def stop(self, request, instance_name=None):
        UserSessionManager().validate_admin_session(request.COOKIES.get("ebiokitsession"))

        service_instance = Application.objects.filter(instance_name=instance_name)[:1]
        if (len(service_instance) == 0):
            return JsonResponse({'success': False, 'error_message': 'Service instance cannot be found'})

        p = subprocess.Popen(osPath.join(osPath.dirname(osPath.realpath(__file__)), '../admin_tools/service') + " " + instance_name + " stop", stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        returncode = p.returncode
        success = (returncode == 0)
        return JsonResponse({'success': success, "stdout": output, 'stderr': err})

    @detail_route(renderer_classes=[renderers.JSONRenderer])
    def restart(self, request, instance_name=None):
        UserSessionManager().validate_admin_session(request.COOKIES.get("ebiokitsession"))

        service_instance = Application.objects.filter(instance_name=instance_name)[:1]
        if (len(service_instance) == 0):
            return JsonResponse({'success': False, 'error_message': 'Service instance cannot be found'})

        p = subprocess.Popen(osPath.join(osPath.dirname(osPath.realpath(__file__)), '../admin_tools/service') + " " + instance_name + " restart", stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        returncode = p.returncode
        success = (returncode == 0)
        return JsonResponse({'success': success, "stdout": output, 'stderr': err})

    @detail_route(renderer_classes=[renderers.JSONRenderer])
    def enable(self, request, instance_name=None):
        UserSessionManager().validate_admin_session(request.COOKIES.get("ebiokitsession"))

        application_instance = self.get_object()
        application_instance.enabled = True
        application_instance.save()
        return JsonResponse({'enabled': application_instance.enabled})

    @detail_route(renderer_classes=[renderers.JSONRenderer])
    def disable(self, request, instance_name=None):
        UserSessionManager().validate_admin_session(request.COOKIES.get("ebiokitsession"))

        application_instance = self.get_object()
        application_instance.enabled = False
        application_instance.save()
        return JsonResponse({'enabled': application_instance.enabled})

    #---------------------------------------------------------------
    #- OTHER FUNCTIONS
    #---------------------------------------------------------------

    def read_settings(self, request):
        settings = request.data.get("settings", {})
        settings["tmp_dir"] = Settings.objects.get(name="tmp_dir").value.rstrip("/") + "/"
        settings["ebiokit_data_location"] = Settings.objects.get(name="ebiokit_data_location").value.rstrip("/") + "/"
        settings["nginx_data_location"] = Settings.objects.get(name="nginx_data_location").value.rstrip("/") + "/"
        settings["ebiokit_host"] = Settings.objects.get(name="ebiokit_host").value
        settings["ebiokit_password"] = Settings.objects.get(name="ebiokit_password").value
        settings["platform"] = Settings.objects.get(name="platform").value

        remote_servers = RemoteServer.objects.values()
        settings["available_remote_servers"] = []
        for server in remote_servers:
            settings["available_remote_servers"].append({'name' : server.get("name"), 'url' : server.get("url")})
        server = RemoteServer.objects.get(enabled=True)
        settings["remote_server"] = {'name' : server.name, 'url' : server.url}

        admin_users = User.objects.filter(role = "admin").values()
        settings["admin_users"] = []
        for user in list(admin_users):
            settings["admin_users"].append(user.get("email"))
        settings["admin_users"] = ",".join(settings["admin_users"])
        return settings

    def update_settings(self, request):
        settings = request.data.get("settings", {})

        prev_value = Settings.objects.get(name="tmp_dir")
        if settings["tmp_dir"] != "" and settings["tmp_dir"] != prev_value.value.rstrip("/") + "/":
            prev_value.value = settings["tmp_dir"].rstrip("/") + "/"
            prev_value.save()

        prev_value = Settings.objects.get(name="ebiokit_data_location")
        if settings["ebiokit_data_location"] != "" and settings["ebiokit_data_location"] != prev_value.value.rstrip("/") + "/":
            prev_value.value = settings["ebiokit_data_location"].rstrip("/") + "/"
            prev_value.save()

        prev_value = Settings.objects.get(name="nginx_data_location")
        if settings["nginx_data_location"] != "" and settings["nginx_data_location"] != prev_value.value.rstrip("/") + "/":
            prev_value.value = settings["nginx_data_location"].rstrip("/") + "/"
            prev_value.save()

        prev_value = Settings.objects.get(name="ebiokit_host")
        if settings["ebiokit_host"] != "" and settings["ebiokit_host"] != prev_value.value:
            prev_value.value = settings["ebiokit_host"]
            prev_value.save()

        prev_value = Settings.objects.get(name="ebiokit_password")
        if settings["ebiokit_password"] != "" and settings["ebiokit_password"] != prev_value.value:
            prev_value.value = settings["ebiokit_password"]
            prev_value.save()

        prev_value = Settings.objects.get(name="platform")
        if settings["platform"] != "" and settings["platform"] != prev_value.value:
            prev_value.value = settings["platform"]
            prev_value.save()

        prev_value = RemoteServer.objects.get(enabled=True)
        if settings["remote_server"]["name"] != "" and settings["remote_server"]["name"] != prev_value.name:
            if settings["remote_server"]["url"] != "" and settings["remote_server"]["url"] != prev_value.url:
                prev_value.enabled = False
                prev_value.save()

                try:
                    exist = RemoteServer.objects.get(url=settings["remote_server"]["url"])
                    exist.name = settings["remote_server"]["name"]
                    exist.url = settings["remote_server"]["url"]
                    exist.enabled = True
                    exist.save()
                except:
                    new_server = RemoteServer(name=settings["remote_server"]["name"], url=settings["remote_server"]["url"], enabled=True)
                    new_server.save()

        if settings.has_key("admin_users") and settings["admin_users"] != "":
            # First invalidate the previous admin users
            admin_users = User.objects.filter(role="admin")
            prev_admin_users = []
            for user in admin_users:
                prev_admin_users.append(user.email)
                user.role = "user"
                user.save()

            admin_users = settings.get("admin_users", "").replace(" ","").split(",")
            valid = 0
            for user in admin_users:
                try:
                    user = User.objects.get(email=user)
                    user.role = "admin"
                    user.save()
                    valid += 1
                except:
                    pass
            # If none user was valid, restore previous admin users
            if valid == 0:
                for user in prev_admin_users:
                    try:
                        user = User.objects.get(email=user)
                        user.role = "admin"
                        user.save()
                    except:
                        pass
