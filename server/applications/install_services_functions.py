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

docker_pull_handler
download_file_handler
checksum_data_handler
extract_data_handler
register_service_handler
clean_data_handler
stop_service_handler
docker_rmi_handler
unregister_service_handler
remove_service_data_handler
"""

import subprocess
import json
import sys
import os
import django
from shutil import rmtree
import requests


def docker_pull_handler(task_id, docker_name, settings=None):
    """
    This function handles the tasks "docker pull" to install new docker images.
    #TODO: version param?
    :param task_id:
    :param docker_name:
    :param settings:
    :return:
    """
    try:
        working_dir = get_job_directory(settings.get("tmp_dir"), task_id)
        log(working_dir, "docker_pull_handler - Pulling image " + docker_name + "...", task_id)
        command = "docker pull " + docker_name
        output = subprocess.check_output(['bash', '-c', command])
        log(working_dir, "docker_pull_handler - Docker image successfully downloaded. " + output, task_id)
        return True
    except Exception as e:
        log(working_dir, "docker_pull_handler - Failed: " + str(e), task_id)
        raise e


def download_file_handler(task_id, url, settings):
    """
    This function handles the tasks "download data" to download remote data from centralhub
    #TODO: version param?
    :param task_id:
    :param url:
    :param settings:
    :return:
    """
    try:
        working_dir = get_job_directory(settings.get("tmp_dir"), task_id)
        log(working_dir, "download_file_handler - Downloading file from " + url, task_id)
        command = "wget --directory-prefix=" + working_dir + " -c --retry-connrefused --tries=3 --timeout=5 --passive-ftp " + url
        output = subprocess.check_output(['bash', '-c', command])
        log(working_dir, "download_file_handler - File successfully downloaded. " + output, task_id)
        return True
    except Exception as e:
        log(working_dir, "download_file_handler - Failed: " + str(e), task_id)
        raise e


def checksum_data_handler(task_id, settings=None):
    """
    This function is used to check the integrity of a set of downloaded files
    :param task_id:
    :param settings:
    :return:
    """
    try:
        working_dir = get_job_directory(settings.get("tmp_dir"), task_id)
        log(working_dir, "checksum_data_handler - Checksum files", task_id)
        command = "md5sum " + working_dir + "/*.tar.bz2* > " + working_dir + "/checksum2.txt"
        log(working_dir, "checksum_data_handler - Comparing obtained checksum vs. expected checksum", task_id)
        output = subprocess.check_output(['bash', '-c', command])
        command = "awk 'NR==FNR{c[$1]++; next};c[$1] == 0{print $0; exit 1}' " + working_dir + "/checksum.txt " + working_dir + "/checksum2.txt"
        output = subprocess.check_output(['bash', '-c', command])
        log(working_dir, "checksum_data_handler - Done: " + output, task_id)
        return True
    except Exception as e:
        log(working_dir, "checksum_data_handler - Failed: " + str(e), task_id)
        raise e


def extract_data_handler(task_id, settings=None):
    """
    This function is used to extract the compressed data for an application.
    By default data is compressed in tar.bz2 and splitted in multiple chunks
    :param task_id:
    :param settings:
    :return:
    """
    try:
        working_dir = get_job_directory(settings.get("tmp_dir"), task_id)
        files = [x for x in os.listdir(working_dir) if len(x) >= 5 and x[-5:] == "_0000"]
        if len(files) > 0:
            # First extract the data to the corresponding directory
            log(working_dir, "extract_data_handler - Merging chunks", task_id)
            command = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../admin_tools/data_manager.sh') + ' "combine" "' + working_dir + '/application_data.tar.bz2" "' + working_dir + '/application_data"'
            output = subprocess.check_output(['bash', '-c', command])
            log(working_dir, "extract_image_data_handler - Done. " + output, task_id)
            log(working_dir, "extract_image_data_handler - Extracting application data", task_id)
            command = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../admin_tools/data_manager.sh') + ' "extract" "' + settings.get("ebiokit_data_location") + 'ebiokit-data/' + settings.get("INSTANCE_NAME") + '/" "' + working_dir + '" "application_data.tar.bz2"'
            output = subprocess.check_output(['bash', '-c', command])
            log(working_dir, "extract_data_handler - Done. " + output, task_id)

        log(working_dir, "extract_data_handler - Extracting service data", task_id)
        os.makedirs(working_dir + '/service_conf')
        command = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../admin_tools/data_manager.sh') + ' "extract" "' + working_dir + '/service_conf" "' + working_dir + '" "service_conf.tar.bz2"'
        log(working_dir, "extract_data_handler - Extracting service data" + command, task_id)
        output = subprocess.check_output(['bash', '-c', command])
        log(working_dir, "extract_data_handler - Done: " + output, task_id)
        return True
    except Exception as e:
        log(working_dir, "extract_data_handler - Failed: " + str(e), task_id)
        raise e


def register_service_handler(task_id, instance_name=None, settings=None):
    """
    This function registers a new service in the ebiokit environment.
    First we read the service information and add a new entry in the database.
    Then we adapt and copy the proxy rules.
    Finally, we adapt and copy the launcher (docker compose file) and
    the uninstall instructions.
    """
    try:
        #TODO dockers param?
        # First register the new service in the database
        working_dir = get_job_directory(settings.get("tmp_dir"), task_id)
        log(working_dir, "register_service_handler - Loading service json data...", task_id)
        with open(working_dir + '/service_conf/service.json') as data_file:
            data = json.load(data_file)

        log(working_dir, "register_service_handler - Add service to database...", task_id)
        # Load DJANGO environment to access databases
        # TODO: USE DATABASE DIRECTLY AND REMOVE DEPENDECY FOR DJANGO
        sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
        django.setup()
        from applications.models import Application

        try:
            service = Application.objects.get(instance_name=instance_name)
            if service is None:
                log(working_dir, "register_service_handler - Service was not in database...", task_id)
                raise Exception("Object not found in db")
            else:
                log(working_dir, "register_service_handler - Service was already in database...", task_id)
        except Exception as e:
            service = Application()

        service.instance_name = instance_name
        service.title = settings.get("INSTANCE_TITLE", data.get("title"))
        service.description = data.get("description")
        service.categories = data.get("categories")
        service.version = data.get("version")
        service.service = data.get("service")
        service.port = ",".join(get_service_ports(settings))
        service.website = "<HOST_NAME>:" + get_service_ports(settings)[0]
        #TODO: tipo?
        # service.type = data.get("type")
        service.raw_options = json.dumps(settings, ensure_ascii=False)
        service.save()

        settings["INSTANCE_DOCKERS"] = data.get("dockers").replace(",", "#")
        settings["DATA_LOCATION"] = os.path.join(settings.get("ebiokit_data_location"), "ebiokit-data")

        # Now adapt the settings for the proxy rules and copy them to the correspoding directory
        log(working_dir, "register_service_handler - Registering service in proxy", task_id)
        copy_and_replace(working_dir + "/service_conf/proxy.upstream", settings.get("nginx_data_location") + instance_name + ".upstream", replacements=settings)
        copy_and_replace(working_dir + "/service_conf/proxy.conf", settings.get("nginx_data_location") + instance_name + ".conf", replacements=settings)

        # Now copy the launcher file (docker-compose) to auto-launch the service on boot
        log(working_dir, "register_service_handler - Add launcher file", task_id)
        command = "mkdir -p " + settings.get("ebiokit_data_location") + "ebiokit-services/launchers/" + instance_name
        output = subprocess.check_output(['bash', '-c', command])
        copy_and_replace(working_dir + "/service_conf/service.launcher", settings.get("ebiokit_data_location") + "ebiokit-services/launchers/" + instance_name + "/docker-compose.yml", replacements=settings)
        create_env_file(settings.get("ebiokit_data_location") + "ebiokit-services/launchers/" + instance_name, settings)

        # Save the auto-remove instructions
        log(working_dir, "register_service_handler - Add uninstall instructions", task_id)
        copy_and_replace(working_dir + "/service_conf/uninstall.json", settings.get("ebiokit_data_location") + "ebiokit-services/uninstallers/" + instance_name + ".json", replacements=settings)

        return True
    except Exception as e:
        log(working_dir, "register_service_handler - Failed: " + str(e), task_id)
        raise e


def clean_data_handler(task_id, settings=None, full=False):
    """
    This function cleans all the temporary data.
    :param task_id:
    :param settings:
    :return:
    """
    try:
        working_dir = get_job_directory(settings.get("tmp_dir"), task_id)
        #TODO remove previous version of docker? docker_name param?
        # if docker_name != None:
        #     print "Removing previous version for image " + docker_name + "..."
        #     command = "docker rmi ebiokit/" + docker_name + ":backup"
        #     ebiokit_remote_launcher(command, settings)
        log(working_dir, "clean_data_handler - Removing temporal data...", task_id)
        if os.path.exists(working_dir):
            if full:
                rmtree(working_dir)
            else:
                for filename in os.listdir(working_dir):
                    filename = working_dir.rstrip("/") + "/" + filename
                    # If is a directory, remove it
                    if os.path.isdir(filename):
                        rmtree(filename)
                    elif ".log" not in filename:
                        os.remove(filename)
        return True
    except Exception as e:
        log(working_dir, "clean_data_handler - Failed: " + str(e), task_id)
        raise e


def stop_service_handler(task_id, instance_name=None, dockers="", settings=None):
    """
    This function stops an instance of an application (docker).
    :param task_id:
    :param instance_name:
    :param dockers:
    :param settings:
    :return:
    """
    try:
        working_dir = get_job_directory(settings.get("tmp_dir"), task_id)
        #STOP THE CONTAINERS
        log(working_dir, "stop_service_handler - Stopping docker containers...", task_id)
        ebiokit_remote_launcher("service stop", instance_name, settings, ignore=True)
        return True
    except Exception as e:
        log(working_dir, "stop_service_handler - Failed: " + str(e), task_id)
        raise e


def docker_rmi_handler(task_id, instance_name=None, dockers="", settings=None):
    try:
        working_dir = get_job_directory(settings.get("tmp_dir"), task_id)
        log(working_dir, "docker_rmi_handler - Removing docker containers...", task_id)
        ebiokit_remote_launcher("service rm", instance_name, settings, ignore=True)

        #TRY TO REMOVE DOCKER IMAGE
        log(working_dir, "docker_rmi_handler - Removing docker images (if possible)...", task_id)
        dockers = dockers.split("#")
        for docker in dockers:
            if docker != "":
                ebiokit_remote_launcher("service rmi", instance_name, settings, ignore=True)
    except Exception as e:
        log(working_dir, "docker_rmi_handler - Failed: " + str(e), task_id)
        raise e


def unregister_service_handler(task_id, instance_name=None, dockers="", settings=None):
    connection = None
    try:
        working_dir = get_job_directory(settings.get("tmp_dir"), task_id)
        #UNREGISTER THE SERVICE (REMOVE FROM DB)
        log(working_dir, "unregister_service_handler - Removing service from database...", task_id)
        #TODO: aqui
        abspath = os.path.dirname(os.path.abspath(__file__))
        import sqlite3
        connection = sqlite3.connect(abspath.rstrip("/") + "/../db.sqlite3")
        cursor = connection.cursor()
        cursor.execute('DELETE FROM applications_application WHERE instance_name="' + instance_name + '"')
        connection.commit()
    except Exception as e:
        log(working_dir, "unregister_service_handler - Failed: " + str(e), task_id)
        raise e
    finally:
        try:
            connection.close()
        except Exception as e:
            raise e


def remove_service_data_handler(task_id, instance_name=None, dockers="", settings=None):
    try:
        working_dir = get_job_directory(settings.get("tmp_dir"), task_id)
        #REMOVE THE PROX.Y CONF
        if os.path.isfile(settings.get("nginx_data_location") + instance_name + ".upstream"):
            log(working_dir, "remove_service_data_handler - Delete the NGINX UPSTREAM file...", task_id)
            os.remove(settings.get("nginx_data_location") + instance_name + ".upstream")
        if os.path.isfile(settings.get("nginx_data_location") + instance_name + ".conf"):
            log(working_dir, "uninstall_service_handler_part_1 - Delete the NGINX CONF file...", task_id)
            os.remove(settings.get("nginx_data_location") + instance_name + ".conf")
        #REMOVE THE LAUNCHER
        if os.path.isfile(settings.get("ebiokit_data_location") + "ebiokit-services/launchers/" + instance_name + "/docker-compose.yml"):
            log(working_dir, "remove_service_data_handler - Delete the launcher file...", task_id)
            os.remove(settings.get("ebiokit_data_location") + "ebiokit-services/launchers/" + instance_name + "/docker-compose.yml")
            os.remove(settings.get("ebiokit_data_location") + "ebiokit-services/launchers/" + instance_name + "/.env")
            os.rmdir(settings.get("ebiokit_data_location") + "ebiokit-services/launchers/" + instance_name)
        #REMOVE THE UNINSTALLER
        if os.path.isfile(settings.get("ebiokit_data_location") + "ebiokit-services/uninstallers/" + instance_name + ".json"):
            log(working_dir, "remove_service_data_handler - Delete the uninstaller file...", task_id)
            os.remove(settings.get("ebiokit_data_location") + "ebiokit-services/uninstallers/" + instance_name + ".json")
        #REMOVE THE DATA FILEs
        if not settings.get("keep_data", False) and os.path.isdir(settings.get("ebiokit_data_location") + "ebiokit-data/" + instance_name):
            log(working_dir, "remove_service_data_handler - Delete the instance data...", task_id)
            command = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../admin_tools/data_manager.sh') + ' "remove" ' + settings.get("ebiokit_data_location") + "ebiokit-data/" + instance_name + "/"
            output = subprocess.check_output(['bash', '-c', command])
            log(working_dir, "remove_service_data_handler - Done: " + output, task_id)
    except Exception as e:
        log(working_dir, "remove_service_data_handler - Failed: " + str(e), task_id)
        raise e


def get_job_directory(tmp_dir, task_id, settings=None):
    jobID = task_id.split("_")[0]
    wd = os.path.join(tmp_dir, jobID)
    if not os.path.exists(wd):
        os.makedirs(wd)
    return wd


def copy_and_replace(source_file, target_file, replacements=None):
    """
    This function copies the source file to the given target destination
    and then replaces the content for the target file using the provided
    list of replacements (replacements must be surrounded by "$${the_value_to_replace}")
    """
    source_file = open(source_file, 'r')
    target_file = open(target_file, 'w')
    if replacements is not None:
        for line in source_file:
            for key, value in replacements.iteritems():
                line = line.replace("$${" + key + "}", str(value))
            target_file.write(line)
    else:
        target_file.write(source_file.read())
    source_file.close()
    target_file.close()


def create_env_file(target_dir, data):
    """
    This function creates the .env file with the settings for the docker-compose
    """
    target_file = open(os.path.join(target_dir, ".env"), 'w')
    for key, value in data.iteritems():
        target_file.write(key + "=" + str(value) + "\n")
    target_file.close()


def log(working_dir, message, task_id=""):
    print task_id + " - " + message
    if working_dir != None:
        log_file = open(working_dir + "/" + task_id + ".log", 'a')
        log_file.write(task_id + " - " + message + "\n")
        log_file.close()


def ebiokit_remote_launcher(command, instance_name, settings, ignore=False):
    data_location = settings.get("ebiokit_data_location") + 'ebiokit-data/' + instance_name + '/'
    command = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../admin_tools/service_tools/ebiokit_launcher.sh') + ' "' + settings.get("platform") + '" "' + command + '" "' + instance_name + '" "' + data_location + '"'
    error = ""
    try:
        p = subprocess.Popen(['bash', '-c', command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (output, err) = p.communicate()
    except Exception as ex:
        if ignore == True:
            pass
        else:
            raise ex
    return output, err


def get_service_ports(settings):
    ports_aux = {}
    ports = []
    port_index_aux = 99
    keys = settings.keys()
    for key in keys:
        if key.startswith("INSTANCE_PORT_"):
            try:
                port_index = int(key.replace("INSTANCE_PORT_", ""))
            except:
                port_index_aux+=1
                port_index = port_index_aux
            ports_aux[port_index] = settings.get(key)

    keys = ports_aux.keys()
    keys.sort()
    for key in keys:
        ports.append(str(ports_aux[key]))
    return ports


def functionWrapper(taks_id, command):
    print "Task " + taks_id + " started..."
    output = subprocess.check_output(['bash', '-c', command])
    print "Task " + taks_id + " finished"


def prepare_upgrade_handler(task_id, instance_name=None, keep_data="keep", script_url=None, settings=None):
    working_dir = get_job_directory(settings.get("tmp_dir"), task_id)
    log(working_dir, "prepare_upgrade_handler - Running pre-upgrading scripts...", task_id)

    if keep_data == "keep" and os.path.isfile(settings.get("ebiokit_data_location") + "ebiokit-services/init-scripts/" + instance_name + ".init"):
        # COPY INIT FILE IF DATA WILL BE KEPT AND EXISTS
        log(working_dir, "prepare_upgrade_handler - Copying VDI init file...", task_id)
        copy_and_replace(settings.get("ebiokit_data_location") + "ebiokit-services/init-scripts/" + instance_name + ".init", working_dir + "/service.init_back", settings)
    try:
        log(working_dir, "prepare_upgrade_handler - Downloading pre-upgrade script...", task_id)
        r = requests.get(script_url)
        with open(working_dir + 'pre-upgrade.sh', 'wb') as output:
            output.write(r.content)
    except Exception:
        log(working_dir, "prepare_upgrade_handler - No pre-upgrade script available", task_id)
        return True # NOT AVAILABLE, DO NOTHING
    #TODO: SET PARAMETERS (SERVICE NAME)
    #TODO: COPY TO COMMON DATA
    #TODO: RUN REMOTELY

    return True


def post_upgrade_handler(task_id, instance_name=None, keep_data="keep", script_url=None, settings=None):
    working_dir = get_job_directory(settings.get("tmp_dir"), task_id)
    log(working_dir, "post_upgrade_handler - Running post-upgrading scripts...", task_id)

    if keep_data == "keep" and os.path.isfile(working_dir + "/service.init_back"):
        # COPY INIT FILE IF DATA WILL BE KEPT AND EXISTS
        log(working_dir, "post_upgrade_handler - Restoring VDI init file...", task_id)
        copy_and_replace(working_dir + "/service.init_back", settings.get("ebiokit_data_location") + "ebiokit-services/init-scripts/" + instance_name + ".init", settings)
    try:
        log(working_dir, "post_upgrade_handler - Downloading post-upgrade script...", task_id)
        r = requests.get(script_url)
        with open(working_dir + 'post-upgrade.sh', 'wb') as output:
            output.write(r.content)
    except Exception:
        log(working_dir, "post_upgrade_handler - No post-upgrade script available", task_id)
        return True #NOT AVAILABLE, DO NOTHING
    #TODO: SET PARAMETERS (SERVICE NAME)
    #TODO: COPY TO COMMON DATA
    #TODO: RUN REMOTELY

    return True


def backup_data_handler(jobID, instance_name, settings=None):
    #version = "latest",
    #TODO: GET INSTANCE BY instance_name

    # working_dir = get_job_directory(settings.get("tmp_dir"), jobID)
    # print "Renaming previous image " + docker_name + "..."
    # command = 'docker rmi ebiokit/' + docker_name + ':backup'
    # try:
    #     subprocess.check_output(['bash', '-c', command])
    # except Exception as exc:
    #     pass
    #
    # command = 'docker tag ebiokit/' + docker_name + ':' + version + ' ebiokit/' + docker_name + ':backup'
    # try:
    #     subprocess.check_output(['bash', '-c', command])
    # except Exception as exc:
    #     pass
    #
    # print "Creating backup for current data..."
    #TODO: backup data

    return True
