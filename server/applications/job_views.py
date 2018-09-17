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

import json
import requests
from django.http import JsonResponse
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.decorators import detail_route

import install_services_functions
from models import Application, RemoteServer, Job, Task, Settings
from resources.UserSessionManager import UserSessionManager
# from resources.pysiq_api import enqueue, check_status, get_result
import resources.pysiq_api as pysiq
from serializers import JobSerializer
from os import path as osPath
import subprocess

class JobViewSet(viewsets.ModelViewSet):
    """ ViewSet for viewing and editing Application objects """
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    lookup_field = "id"

    #---------------------------------------------------------------
    #- MANIPULATE INSTALLED SERVICES
    #---------------------------------------------------------------
    @detail_route(renderer_classes=[renderers.JSONRenderer])
    def prepare_install(self, request, instance_name=None):
        """
        This function retrieves from the centralhub the installation settings for a given service (i.e. the content for
        the form that we use to configure the service: name, port, etc.)
        :param request:
        :param instance_name:
        :return:
        """
        # -------------------------------------------------------------------------------------------------------------
        # Step 0. First we validate that user is a valid ADMIN user
        UserSessionManager().validate_admin_session(request.COOKIES.get("ebiokitsession"))
        # -------------------------------------------------------------------------------------------------------------
        # Step 1. Now send the request to the centralhub
        main_remote_server = RemoteServer.objects.get(enabled=1)
        r = requests.get(main_remote_server.url.rstrip("/") + "/api/" + instance_name + "/prepare-install")
        # -------------------------------------------------------------------------------------------------------------
        # Step 2. If we can't find a valid settings file for requested version, fail
        if r.status_code != 200 or r.json().get("success") == False:
            response = JsonResponse({'success': False, 'error_message' : 'Unable to retrieve installation settings for service from ' + main_remote_server.name})
            response.status_code = 500
            return response
        # -------------------------------------------------------------------------------------------------------------
        # Step 3. Finally check al the services that are already installed and get the invalid settings to avoid collisions
        invalid_options = self.get_current_settings()

        return JsonResponse({'success': True, 'settings' : r.json().get("settings"), "invalid_options" : invalid_options})

    @detail_route(renderer_classes=[renderers.JSONRenderer])
    def prepare_upgrade(self, request, instance_name=None):
        """
        This function retrieves from the centralhub the upgrading settings for a given service (i.e. the content for
        the form that we use to configure the service: name, port, etc.)
        :param request:
        :param instance_name:
        :return:
        """
        # -------------------------------------------------------------------------------------------------------------
        # Step 0. First we validate that user is a valid ADMIN user
        UserSessionManager().validate_admin_session(request.COOKIES.get("ebiokitsession"))
        # -------------------------------------------------------------------------------------------------------------
        # Step 1. Now we get the requested version from params
        candidate_version = request.GET.get('candidate', '')
        # -------------------------------------------------------------------------------------------------------------
        # Step 2. Now send the request to the centralhub
        main_remote_server = RemoteServer.objects.get(enabled=1)
        r = requests.get(main_remote_server.url.rstrip("/") + "/api/" + candidate_version + "/prepare-install")
        # -------------------------------------------------------------------------------------------------------------
        # Step 3. If we can't find a valid settings file for requested version, fail
        if r.status_code != 200 or r.json().get("success") == False:
            response = JsonResponse({'success': False, 'error_message': 'Unable to retrieve upgrading settings for service from ' + main_remote_server.name})
            response.status_code = 500
            return response
        # -------------------------------------------------------------------------------------------------------------
        # Step 4. Otherwise, we need to fill the settings for installation with the values for the current instance (the one that we
        #         want to upgrade)
        # Step 4.1 First get the service from database
        service = Application.objects.filter(instance_name=instance_name)[:1]
        if len(service) == 0:
            response = JsonResponse({'success': False, 'error_message' : 'Unable to retrieve installation settings for service from ' + main_remote_server.name})
            response.status_code = 500
            return response
        # Step 4.2 Now load the installation settings that are saved in db
        current_options = json.loads(service[0].raw_options)
        settings = r.json().get("settings")
        # Step 4.3 Finally replace the default values by the corresponding values in current instance
        for setting in settings:
            setting["default"] = current_options.get(setting["name"], setting.get("default", ""))
        # -------------------------------------------------------------------------------------------------------------
        # Step 5. Finally check al the services that are already installed and get the invalid settings to avoid collisions
        invalid_options = self.get_current_settings(ignore=[instance_name])

        return JsonResponse({'success': True, 'settings' : settings, "invalid_options" : invalid_options})

    @detail_route(renderer_classes=[renderers.JSONRenderer])
    def install(self, request, instance_name=None):
        # -------------------------------------------------------------------------------------------------------------
        # Step 0. First we validate that user is a valid ADMIN user and read the params from request
        UserSessionManager().validate_admin_session(request.COOKIES.get("ebiokitsession"))
        settings = self.read_settings(request)
        # -------------------------------------------------------------------------------------------------------------
        # Step 1. Get the installation instructions from the centralhub
        main_remote_server = RemoteServer.objects.get(enabled=1)
        r = requests.get(main_remote_server.url.rstrip("/") + "/api/" + instance_name + "/install")
        # If we can't find a valid settings file for requested version, fail
        if r.status_code != 200 or r.json().get("success") == False:
            response = JsonResponse({'success': False, 'error_message' : 'Unable to retrieve installation instructions for service from ' + main_remote_server.name})
            response.status_code = 500
            return response
        instructions = r.json().get("instructions")
        # -------------------------------------------------------------------------------------------------------------
        # Step 2. Create a new instance of job and register it in the database.
        job = Job()
        job.name = instructions.get("job_name")
        job.id = self.get_new_job_id()
        job.date = datetime.datetime.now().strftime("%Y%m%d%H%M")
        job.save()
        # -------------------------------------------------------------------------------------------------------------
        # Step 3. For each task in the job, create a new instance of Task and register it in the database.
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
        # -------------------------------------------------------------------------------------------------------------
        # Step 4. Finally, enqueue all the tasks in the queue
        try:
            for task in tasks:
                if task.command != "":
                    pysiq.enqueue(
                        fn="functionWrapper",
                        args=(task.name + '(' + task.id + ')', task.command),
                        task_id=task.id,
                        depend=(None if len(task.depend) == 0 else task.depend.split(",")),
                        incompatible=None if len(task.incompatible) == 0 else task.incompatible.split(","),
                        server=settings["queue_server"],
                        port=settings["queue_port"]
                    )
                else:
                    pysiq.enqueue(
                        fn=task.function,
                        args=[task.id] + (task.params.split(",") if task.params != "" else []) + [settings],
                        task_id=task.id,
                        depend=(None if len(task.depend) == 0 else task.depend.split(",")),
                        incompatible=(None if len(task.incompatible) == 0 else task.incompatible.split(",")),
                        server=settings["queue_server"],
                        port=settings["queue_port"]
                    )

            return JsonResponse({'success': True, 'job_id': job.id})
        except Exception as e:
            return JsonResponse({'success': False, 'job_id': job.id, 'error_message': "Unreachable queue"})

    @detail_route(renderer_classes=[renderers.JSONRenderer])
    def upgrade(self, request, instance_name=None):
        # -------------------------------------------------------------------------------------------------------------
        # Step 0. First we validate that user is a valid ADMIN user and read the params from request
        UserSessionManager().validate_admin_session(request.COOKIES.get("ebiokitsession"))
        # Get the settings for the instance from params
        settings = self.read_settings(request)
        # Now we get the requested version from params
        candidate_version = request.data.get("candidate")
        # -------------------------------------------------------------------------------------------------------------
        # Step 1. Get the installation instructions from the centralhub
        main_remote_server = RemoteServer.objects.get(enabled=1)
        r = requests.get(main_remote_server.url.rstrip("/") + "/api/" + candidate_version + "/upgrade")
        # If we can't find a valid settings file for requested version, fail
        if r.status_code != 200 or r.json().get("success") == False:
            response = JsonResponse({'success': False, 'error_message' : 'Unable to retrieve upgrading instructions for service from ' + main_remote_server.name})
            response.status_code = 500
            return response
        instructions_1 = r.json().get("instructions")
        # Step 2. Get the uninstall instructions from the data repository
        service = Application.objects.filter(instance_name=instance_name)[:1]
        if (len(service) == 0):
            return JsonResponse({'success': False, 'error_message': 'Service instance cannot be found'})
        instructions_2 = json.loads(open(settings.get("ebiokit_data_location") + "ebiokit-services/uninstallers/" + instance_name + ".json", "r").read())

        # Locate the instruction that indicates the position where uninstall instruction should be inserted
        uninstall_id = -1
        uninstall_pos = -1
        uninstall_depend = []
        tasks = instructions_1.get("tasks")
        for i in range(len(tasks)):
            task = tasks[i]
            if task.get("function") == "uninstall_service":
                uninstall_id = task.get("id")
                settings["keep_data"] = "keep_data" in task.get("params")
                uninstall_depend = tasks[i].get("depend")
                uninstall_pos = i
                del tasks[i] # Remove the instruction
                break

        if uninstall_id != -1:
            # Now update the ids and dependencies for all the tasks in "uninstall" instructions
            tasks = instructions_2.get("tasks")
            max_id=-1
            for task in tasks:
                # E.g if id is 2 and uninstall_id is 8, new ID would be 10
                task["id"] = task["id"] + uninstall_id
                max_id = max(max_id, task.get("id"))
                # If no dependency was indicated -> now should be the same than uninstall_depend task
                if task.get("depend") is None:
                    task["depend"] = uninstall_depend
                else:
                    # Otherwise, if there are dependencies, update with the new ids (e.g. if depends on tasks 1 and 3 -> new depend. will be 9 and 11).
                    for i in range(len(task["depend"])):
                        task["depend"][i] = task["depend"][i] + uninstall_id
            # Here, uninstall instructions should be ready to be merged
            # But we need first to update all the tasks in "update" instructions where the ID and the dependencies will change do to the new tasks
            tasks = instructions_1.get("tasks")
            for task in tasks:
                # E.g. If we added 4 new tasks (max_id is 11), the original task 9 should be converted to 9 + (11 - 8) = 12
                if task.get("id") > uninstall_id:
                    task["id"] = task["id"] + (max_id - uninstall_id)
                # Now update then dependencies using the same idea. If task 11, depended on 8 and 10 -> now should be 11 and 13
                for i in range(len(task.get("depend", []))):
                    if task["depend"][i] >= uninstall_id:
                        task["depend"][i] = task["depend"][i] + (max_id - uninstall_id)
            # Finally, we merge both lists of instructions
            new_tasks = instructions_1.get("tasks")
            for task in instructions_2.get("tasks"):
                new_tasks.insert(uninstall_pos, task)
                uninstall_pos += 1

        # -------------------------------------------------------------------------------------------------------------
        # Step 2. Create a new instance of job and register it in the database.
        job = Job()
        job.name = instructions_1.get("job_name")
        job.id = self.get_new_job_id()
        job.date = datetime.datetime.now().strftime("%Y%m%d%H%M")
        job.save()
        # -------------------------------------------------------------------------------------------------------------
        # Step 3. For each task in the job, create a new instance of Task and register it in the database.
        tasks = []
        for instruction in instructions_1.get("tasks"):
            if instruction.get("run-if", "upgrade") != "upgrade":
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
                task.params = ','.join([str(x) for x in instruction.get("params")])
                task.params = task.params.replace("$${INSTANCE_NAME}", settings.get("INSTANCE_NAME"))

            task.depend = ",".join((job.id + "_" + str(n)) for n in instruction.get("depend", ""))
            task.incompatible = ",".join(instruction.get("incompatible", ""))
            task.status = "NEW"
            task.save()
            tasks.append(task)
        # -------------------------------------------------------------------------------------------------------------
        # Step 4. Finally, enqueue all the tasks in the queue
        try:
            for task in tasks:
                if task.command != "":
                    pysiq.enqueue(
                        fn="functionWrapper",
                        args=(task.name + '(' + task.id + ')', task.command),
                        task_id=task.id,
                        depend=(None if len(task.depend) == 0 else task.depend.split(",")),
                        incompatible=None if len(task.incompatible) == 0 else task.incompatible.split(","),
                        server=settings["queue_server"],
                        port=settings["queue_port"]
                    )
                else:
                    pysiq.enqueue(
                        fn=task.function,
                        args=[task.id] + (task.params.split(",") if task.params != "" else []) + [settings],
                        task_id=task.id,
                        depend=(None if len(task.depend) == 0 else task.depend.split(",")),
                        incompatible=(None if len(task.incompatible) == 0 else task.incompatible.split(",")),
                        server=settings["queue_server"],
                        port=settings["queue_port"]
                    )

            return JsonResponse({'success': True, 'job_id': job.id})
        except Exception as e:
            return JsonResponse({'success': False, 'job_id': job.id, 'error_message': "Unreachable queue"})

    @detail_route(renderer_classes=[renderers.JSONRenderer])
    def uninstall(self, request, instance_name=None):
        # First we validate that user is a valid ADMIN user
        UserSessionManager().validate_admin_session(request.COOKIES.get("ebiokitsession"))

        settings = self.read_settings(request)
        settings["keep_data"] = False

        # Step 1. Get the uninstall instructions from the data repository
        service = Application.objects.filter(instance_name=instance_name)[:1]
        if (len(service) == 0):
            return JsonResponse({'success': False, 'error_message': 'Service instance cannot be found'})
        instructions = json.loads(open(settings.get("ebiokit_data_location") + "ebiokit-services/uninstallers/" + instance_name + ".json", "r").read())

        # Step 2. Create a new instance of job and register it in the database.
        job = Job()
        job.name = instructions.get("job_name")
        job.id = self.get_new_job_id()
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

        try:
            for task in tasks:
                if task.command != "":
                    pysiq.enqueue(
                        fn="functionWrapper",
                        args=(task.name + '(' + task.id + ')', task.command),
                        task_id=task.id,
                        depend=(None if len(task.depend) == 0 else task.depend.split(",")),
                        incompatible=None if len(task.incompatible) == 0 else task.incompatible.split(","),
                        server=settings["queue_server"],
                        port=settings["queue_port"]
                    )
                else:
                    pysiq.enqueue(
                        fn=task.function,
                        args=[task.id] + (task.params.split(",") if task.params != "" else []) + [settings],
                        task_id=task.id,
                        depend=(None if len(task.depend) == 0 else task.depend.split(",")),
                        incompatible=(None if len(task.incompatible) == 0 else task.incompatible.split(",")),
                        server=settings["queue_server"],
                        port=settings["queue_port"]
                    )
            return JsonResponse({'success': True, 'job_id': job.id})
        except Exception as e:
            return JsonResponse({'success': False, 'job_id': job.id, 'error_message': "Unreachable queue"})

    @detail_route(renderer_classes=[renderers.JSONRenderer])
    def check_job_status(self, request, id=None):
        UserSessionManager().validate_admin_session(request.COOKIES.get("ebiokitsession"))

        jobs = Job.objects.all()

        jobs_list = []
        failed = False
        for job in jobs:
            tasks = Task.objects.filter(job_id=job.id)
            tasks_list = []
            not_finished = 0
            for task in tasks:
                if task.status != 'FINISHED' and task.status != 'FAILED':
                    not_finished += 1
                    try:
                        _status = pysiq.check_status(task.id)
                        # _result = pysiq.get_result(task.id, remove=False)
                    except Exception as ex:
                        failed = True
                    #TODO: EVALUATE RESULT?
                    try:
                        _status = _status.status.upper().replace(" ", "_")
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
            try:
                if not_finished == 0:
                    for task in tasks:
                        pysiq.get_result(task.id, remove=True)
            except Exception as e:
                failed = True

            jobs_list.append({
                'id': job.id,
                'name': job.name,
                'date': job.date,
                'tasks': tasks_list
            })

        return JsonResponse({'success': not failed, 'jobs' : jobs_list, 'error_message' : "Unreachable queue" if failed else ""})

    @detail_route(renderer_classes=[renderers.JSONRenderer])
    def get_job_log(self, request, id=None):
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
    def delete_job(self, request, id=None):
        UserSessionManager().validate_admin_session(request.COOKIES.get("ebiokitsession"))

        job_instance = Job.objects.filter(id=id)[0]
        if job_instance != None:
            tasks = Task.objects.filter(job_id=job_instance.id)
            for task in tasks:
                pysiq.get_result(task.id, remove=True)
                # pysiq.remove_task(task.id)
                task.delete()
            job_instance.delete()

            settings = self.read_settings(request)

            install_services_functions.clean_data_handler(id, settings, full=True)
            return JsonResponse({'success': True})

    #---------------------------------------------------------------
    #- OTHER FUNCTIONS
    #---------------------------------------------------------------

    def get_new_job_id(self):
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
        settings["platform"] = Settings.objects.get(name="platform").value
        try:
            settings["queue_server"] = Settings.objects.get(name="queue_server").value
        except:
            settings["queue_server"] = "localhost"
        try:
            settings["queue_port"] = Settings.objects.get(name="queue_port").value
        except:
            settings["queue_port"] = "4444"

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
