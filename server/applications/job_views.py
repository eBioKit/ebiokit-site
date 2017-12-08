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

import datetime

import requests
from django.http import JsonResponse
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.decorators import detail_route

import install_services_functions
from models import Application, RemoteServer, Job, Task, Settings
from resources.UserSessionManager import UserSessionManager
from serializers import JobSerializer
from resources.PySiQ import Queue
from os import path as osPath
import subprocess

class JobViewSet(viewsets.ModelViewSet):
    """ ViewSet for viewing and editing Application objects """
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    lookup_field = "id"
    N_WORKERS = 4

    queue_instance = Queue()
    queue_instance.enableStdoutLogging()
    queue_instance.start_worker(N_WORKERS)

    #---------------------------------------------------------------
    #- MANIPULATE INSTALLED SERVICES
    #---------------------------------------------------------------
    @detail_route(renderer_classes=[renderers.JSONRenderer])
    def prepareInstall(self, request, instance_name=None):
        UserSessionManager().validate_admin_session(request.COOKIES.get("ebiokitsession"))

        mainRemoteServer = RemoteServer.objects.get(enabled=1)
        r = requests.get(mainRemoteServer.url.rstrip("/") + "/api/" + instance_name + "/prepare-install")
        if r.status_code != 200 or r.json().get("success") == False:
            response = JsonResponse({'success': False, 'error_message' : 'Unable to retrieve installation settings for service from ' + mainRemoteServer.name})
            response.status_code = 500
            return response

        invalid_options = self.get_current_settings()

        return JsonResponse({'success': True, 'settings' : r.json().get("settings"), "invalid_options" : invalid_options})

    @detail_route(renderer_classes=[renderers.JSONRenderer])
    def prepareUpgrade(self, request, instance_name=None):
        UserSessionManager().validate_admin_session(request.COOKIES.get("ebiokitsession"))

        mainRemoteServer = RemoteServer.objects.get(enabled=1)
        candidate = request.GET.get('candidate', '')
        r = requests.get(mainRemoteServer.url.rstrip("/") + "/api/" + candidate + "/prepare-install")
        if r.status_code != 200 or r.json().get("success") == False:
            response = JsonResponse({'success': False, 'error_message' : 'Unable to retrieve installation settings for service from ' + mainRemoteServer.name})
            response.status_code = 500
            return response

        invalid_options = self.get_current_settings(ignore=[instance_name])

        service = Application.objects.filter(instance_name=instance_name)[:1]
        if (len(service) == 0):
            response = JsonResponse({'success': False, 'error_message' : 'Unable to retrieve installation settings for service from ' + mainRemoteServer.name})
            response.status_code = 500
            return response

        import json
        current_options = json.loads(service[0].raw_options)
        settings = r.json().get("settings")

        for setting in settings:
            setting["default"] = current_options.get(setting["name"], setting.get("default", ""))

        return JsonResponse({'success': True, 'settings' : settings, "invalid_options" : invalid_options})

    @detail_route(renderer_classes=[renderers.JSONRenderer])
    def install(self, request, instance_name=None):
        UserSessionManager().validate_admin_session(request.COOKIES.get("ebiokitsession"))

        settings = self.read_settings(request)

        #Step 0. Check machine status
        if not self.isValidMachineStatus(settings):
            return JsonResponse({'success': False, 'error_message': "eBioKit machine is unreachable. Perhaps it is not running?"})

        #Step 1. Get all services from remote server
        mainRemoteServer = RemoteServer.objects.get(enabled=1)
        r = requests.get(mainRemoteServer.url.rstrip("/") + "/api/" + instance_name + "/install")
        if r.status_code != 200 or r.json().get("success") == False:
            response = JsonResponse({'success': False, 'error_message' : 'Unable to retrieve installation instructions for service from ' + mainRemoteServer.name})
            response.status_code = 500
            return response
        instructions = r.json().get("instructions")

        job = Job()
        job.name = instructions.get("job_name")
        job.id = self.getNewJobID()
        job.date = datetime.datetime.now().strftime("%Y%m%d%H%M")
        job.save()

        tasks = []
        for instruction in instructions.get("tasks"):
            if instruction.get("run-if", "install") != "install":
                continue

            task = Task()
            task.id = job.id + "_" + str(instruction.get("id"))
            task.job_id = job.id
            task.name = instruction.get("name")
            if instruction.has_key("command"):
                task.command = instruction.get("command")
            elif instruction.has_key("function"):
                task.function = instruction.get("function")

            if instruction.has_key("params"):
                task.params= ','.join([str(x) for x in instruction.get("params")])
                task.params = task.params.replace("$${INSTANCE_NAME}", settings.get("INSTANCE_NAME"))

            task.depend = ",".join((job.id + "_" + str(n)) for n in instruction.get("depend", ""))
            task.incompatible = ",".join(instruction.get("incompatible", ""))
            task.status = "NEW"
            task.save()
            tasks.append(task)

        for task in tasks:
            if task.command != "":
                self.queue_instance.enqueue(
                    fn=install_services_functions.functionWrapper,
                    args=(task.name + '(' + task.id + ')', task.command),
                    task_id= task.id,
                    depend= None if len(task.depend) == 0 else task.depend.split(","),
                    incompatible= None if len(task.incompatible) == 0 else task.incompatible.split(",")
                )
            else:
                self.queue_instance.enqueue(
                    fn= getattr(install_services_functions, task.function),
                    args=[task.id] + (task.params.split(",") if task.params != "" else []) + [settings],
                    task_id= task.id,
                    depend= None if len(task.depend) == 0 else task.depend.split(","),
                    incompatible= None if len(task.incompatible) == 0 else task.incompatible.split(",")
                )

        return JsonResponse({'success': True, 'job_id': job.id})

    @detail_route(renderer_classes=[renderers.JSONRenderer])
    def upgrade(self, request, instance_name=None):
        UserSessionManager().validate_admin_session(request.COOKIES.get("ebiokitsession"))

        settings = self.read_settings(request)

        #Step 0. Check machine status
        if not self.isValidMachineStatus(settings):
            return JsonResponse({'success': False, 'error_message': "eBioKit machine is unreachable. Perhaps it is not running?"})

        #Step 1. Get all services from remote server
        mainRemoteServer = RemoteServer.objects.get(enabled=1)
        candidate = request.data.get("candidate")
        r = requests.get(mainRemoteServer.url.rstrip("/") + "/api/" + candidate + "/upgrade")
        if r.status_code != 200 or r.json().get("success") == False:
            response = JsonResponse({'success': False, 'error_message' : 'Unable to retrieve upgrading instructions for service from ' + mainRemoteServer.name})
            response.status_code = 500
            return response
        instructions = r.json().get("instructions")

        job = Job()
        job.name = instructions.get("job_name")
        job.id = self.getNewJobID()
        job.date = datetime.datetime.now().strftime("%Y%m%d%H%M")
        job.save()

        tasks = []
        for instruction in instructions.get("tasks"):
            if instruction.get("run-if", "install") != "install":
                continue

            task = Task()
            task.id = job.id + "_" + str(instruction.get("id"))
            task.job_id = job.id
            task.name = instruction.get("name")
            if instruction.has_key("command"):
                task.command = instruction.get("command")
            elif instruction.has_key("function"):
                task.function = instruction.get("function")

            if instruction.has_key("params"):
                task.params= ','.join([str(x) for x in instruction.get("params")])
                task.params = task.params.replace("$${INSTANCE_NAME}", settings.get("INSTANCE_NAME"))

            task.depend = ",".join((job.id + "_" + str(n)) for n in instruction.get("depend", ""))
            task.incompatible = ",".join(instruction.get("incompatible", ""))
            task.status = "NEW"
            task.save()
            tasks.append(task)

        for task in tasks:
            if task.command != "":
                self.queue_instance.enqueue(
                    fn=install_services_functions.functionWrapper,
                    args=(task.name + '(' + task.id + ')', task.command),
                    task_id= task.id,
                    depend= None if len(task.depend) == 0 else task.depend.split(","),
                    incompatible= None if len(task.incompatible) == 0 else task.incompatible.split(",")
                )
            else:
                self.queue_instance.enqueue(
                    fn= getattr(install_services_functions, task.function),
                    args=[task.id] + (task.params.split(",") if task.params != "" else []) + [settings],
                    task_id= task.id,
                    depend= None if len(task.depend) == 0 else task.depend.split(","),
                    incompatible= None if len(task.incompatible) == 0 else task.incompatible.split(",")
                )

        return JsonResponse({'success': True, 'job_id': job.id})

    @detail_route(renderer_classes=[renderers.JSONRenderer])
    def uninstall(self, request, instance_name=None):
        UserSessionManager().validate_admin_session(request.COOKIES.get("ebiokitsession"))

        settings = self.read_settings(request)

        #Step 0. Check machine status
        if not self.isValidMachineStatus(settings):
            return JsonResponse({'success': False, 'error_message': "eBioKit machine is unreachable. Perhaps it is not running?"})

        service = Application.objects.filter(instance_name=instance_name)[:1]

        if (len(service) == 0):
            return JsonResponse({'success': False, 'error_message': 'Service instance cannot be found'})

        # Step 1. Get all services from remote server
        import json
        instructions = json.loads(open(settings.get("ebiokit_data_location") + "ebiokit-services/uninstallers/" + instance_name + ".json", "r").read())

        job = Job()
        job.name = instructions.get("job_name")
        job.id = self.getNewJobID()
        job.date = datetime.datetime.now().strftime("%Y%m%d%H%M")
        job.save()

        tasks = []
        for instruction in instructions.get("tasks"):
            task = Task()
            task.id = job.id + "_" + str(instruction.get("id"))
            task.job_id = job.id
            task.name = instruction.get("name")
            if instruction.has_key("command"):
                task.command = instruction.get("command")
            elif instruction.has_key("function"):
                task.function = instruction.get("function")

            if instruction.has_key("params"):
                task.params = ','.join([str(x) for x in instruction.get("params")])

            task.depend = ",".join((job.id + "_" + str(n)) for n in instruction.get("depend", ""))
            task.incompatible = ",".join(instruction.get("incompatible", ""))
            task.status = "NEW"
            task.save()
            tasks.append(task)

        for task in tasks:
            if task.command != "":
                self.queue_instance.enqueue(
                    fn=install_services_functions.functionWrapper,
                    args=(task.name + '(' + task.id + ')', task.command),
                    task_id=task.id,
                    depend=None if len(task.depend) == 0 else task.depend.split(","),
                    incompatible= None if len(task.incompatible) == 0 else task.incompatible.split(",")
                )
            else:
                self.queue_instance.enqueue(
                    fn=getattr(install_services_functions, task.function),
                    args=[task.id] + (task.params.split(",") if task.params != "" else []) + [settings],
                    task_id=task.id,
                    depend=None if len(task.depend) == 0 else task.depend.split(","),
                    incompatible= None if len(task.incompatible) == 0 else task.incompatible.split(",")
                )

        return JsonResponse({'success': True, 'job_id': job.id})

    @detail_route(renderer_classes=[renderers.JSONRenderer])
    def checkJobStatus(self, request, id=None):
        UserSessionManager().validate_admin_session(request.COOKIES.get("ebiokitsession"))

        jobs = Job.objects.all()

        jobs_list = []
        for job in jobs:
            tasks = Task.objects.filter(job_id=job.id)
            tasks_list = []
            not_finished = 0
            for task in tasks:
                if task.status != 'FINISHED' and task.status != 'FAILED':
                    not_finished += 1
                    _status = self.queue_instance.check_status(task.id)
                    _result = self.queue_instance.get_result(task.id, False)
                    #TODO: EVALUATE RESULT
                    try:
                        _status = _status.upper().replace(" ", "_")
                        if task.status != _status:
                            task.status = _status
                            task.save()
                    except Exception as ex:
                        # print ex.message
                        try:
                            _status = _status.name.upper().replace(" ", "_")
                            if task.status != _status:
                                task.status = _status
                                task.save()
                        except:
                            pass

                tasks_list.append({
                    'id': task.id,
                    'name': task.name,
                    'status': task.status
                })

            #REMOVE ALL TASKS FROM QUEUE
            if not_finished == 0:
                for task in tasks:
                    self.queue_instance.get_result(task.id, True)

            jobs_list.append({
                'id': job.id,
                'name': job.name,
                'date': job.date,
                'tasks': tasks_list
            })

        return JsonResponse({'success': True, 'jobs' : jobs_list})


    @detail_route(renderer_classes=[renderers.JSONRenderer])
    def getJobLog(self, request, id=None):
        settings = self.read_settings(request)
        job_id = id.split("_")[0]
        task_id = id

        try:
            file_path = settings["tmp_dir"] + job_id + "/" + task_id  + ".log"
            file = open(file_path, "r")
            content = file.read()
            file.close()
        except Exception:
            content="Log file not found."
        return JsonResponse({'success': True, 'log' : content})

    @detail_route(renderer_classes=[renderers.JSONRenderer])
    def deleteJob(self, request, id=None):
        UserSessionManager().validate_admin_session(request.COOKIES.get("ebiokitsession"))

        job_instance = Job.objects.filter(id=id)[0]
        if job_instance != None:
            tasks = Task.objects.filter(job_id=job_instance.id)
            for task in tasks:
                _result = self.queue_instance.get_result(task.id, True)
                self.queue_instance.remove_task(task.id)
                task.delete()
            job_instance.delete()

            settings = self.read_settings(request)

            install_services_functions.clean_data_handler(id, settings)
            return JsonResponse({'success': True})

    #---------------------------------------------------------------
    #- OTHER FUNCTIONS
    #---------------------------------------------------------------

    def getNewJobID(self):
        #RANDOM GENERATION OF THE JOB ID
        #TODO: CHECK IF NOT EXISTING ID
        import string, random
        jobID = ''.join(random.sample(string.ascii_letters+string.octdigits*5,10))
        return jobID

    def read_settings(self, request):
        settings = request.data.get("settings", {})
        settings["INSTANCE_URL"] = "/" + settings.get("INSTANCE_URL", settings.get("INSTANCE_NAME", "")).strip("/").replace("_", "-") + "/"
        settings["tmp_dir"] = Settings.objects.get(name="tmp_dir").value.rstrip("/") + "/"
        settings["ebiokit_data_location"] = Settings.objects.get(name="ebiokit_data_location").value.rstrip("/") + "/"
        settings["nginx_data_location"] = Settings.objects.get(name="nginx_data_location").value.rstrip("/") + "/"
        settings["ebiokit_host"] = Settings.objects.get(name="ebiokit_host").value
        settings["ebiokit_password"] = Settings.objects.get(name="ebiokit_password").value
        settings["platform"] = Settings.objects.get(name="platform").value
        return settings

    def get_current_settings(self, ignore=None):
        applications = Application.objects.all()

        instance_names = []
        instance_titles = []
        ports = []
        for application in applications:
            if ignore != None and application.instance_name in ignore:
                continue
            instance_titles.append(application.title)
            instance_names.append(application.instance_name)
            ports += application.port.split(",")
        return {"titles" : instance_titles, "instance_names" : instance_names, "ports" : ports}

    def isValidMachineStatus(self, settings):
        command = "status"
        command = osPath.join(osPath.dirname(osPath.realpath(__file__)), '../admin_tools/ebiokit_launcher.sh') + ' "' + settings.get("ebiokit_host") + '" "' + settings.get("ebiokit_password") + '" "' + settings.get("platform") + '" "' + command + '"'
        output = subprocess.check_output(['bash', '-c', command])
        return (output.rstrip() == "RUNNING")
