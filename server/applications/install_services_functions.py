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

import subprocess
from os import path as osPath, listdir as osListdir, remove as osRemoveFile, rmdir as osRemoveDir
import requests
import json

def functionWrapper(taks_id, command):
    print "Task " + taks_id + " started..."
    output = subprocess.check_output(['bash', '-c', command])
    print "Task " + taks_id + " finished"

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

def download_file_handler(task_id, URL, settings):
    working_dir = get_job_directory(settings.get("tmp_dir"), task_id)
    log(working_dir, "download_file_handler - Downloading file from " + URL, task_id)
    command = "wget --directory-prefix=" + working_dir + " -c --retry-connrefused --tries=3 --timeout=5 " + URL
    output = subprocess.check_output(['bash', '-c', command])
    log(working_dir, "download_file_handler - File successfully downloaded. " + output, task_id)
    return True

def checksum_image_data_handler(task_id, settings=None):
    working_dir = get_job_directory(settings.get("tmp_dir"), task_id)
    log(working_dir, "checksum_image_data_handler - Checksum files", task_id)
    command = "md5sum " + working_dir + "/*.7z* > " + working_dir + "/checksum2.txt"
    log(working_dir, "checksum_image_data_handler - Comparing obtained checksum vs. expected checksum", task_id)
    output = subprocess.check_output(['bash', '-c', command])
    command = "awk 'NR==FNR{c[$1]++; next};c[$1] == 0{print $0; exit 1}' " + working_dir + "/checksum.txt " + working_dir + "/checksum2.txt"
    output = subprocess.check_output(['bash', '-c', command])
    log(working_dir, "checksum_image_data_handler - Done: " + output, task_id)
    return True

def docker_pull_handler(task_id, docker_name, settings=None):
    working_dir = get_job_directory(settings.get("tmp_dir"), task_id)
    log(working_dir, "docker_pull_handler - Pulling image " + docker_name + "...", task_id)
    #version param?
    command = "docker pull " + docker_name
    return ebiokit_remote_launcher(command, settings)

def extract_image_data_handler(task_id, settings=None):
    working_dir = get_job_directory(settings.get("tmp_dir"), task_id)

    files = [x for x in osListdir(working_dir) if len(x) >= 7 and x[-7:] == ".7z.001"]
    if len(files) > 0:
        log(working_dir, "extract_image_data_handler - Extracting files", task_id)
        command = "7za e -y -o" + settings.get("ebiokit_data_location") + "ebiokit-data/" + settings.get("INSTANCE_NAME") + " " + working_dir + "/*.7z.001"
        output = subprocess.check_output(['bash', '-c', command])
        log(working_dir, "extract_image_data_handler - Extracting files: " + output, task_id)
        command = "mv " + settings.get("ebiokit_data_location") + "ebiokit-data/" + settings.get("INSTANCE_NAME") + "/*.vdi " + settings.get("ebiokit_data_location") + "ebiokit-data/" + settings.get("INSTANCE_NAME") + ".vdi"
        output = subprocess.check_output(['bash', '-c', command])
        command = "rmdir " + settings.get("ebiokit_data_location") + "ebiokit-data/" + settings.get("INSTANCE_NAME") + "/"
        output = subprocess.check_output(['bash', '-c', command])

    command = "7za e -y -o" + working_dir + "/service_conf " + working_dir + "/service_conf.7z"
    output = subprocess.check_output(['bash', '-c', command])
    log(working_dir, "extract_image_data_handler - Extracting files: " + output, task_id)
    return True

def register_service_handler(task_id, instance_name=None, settings=None):
    #TODO dockers param?
    working_dir = get_job_directory(settings.get("tmp_dir"), task_id)
    log(working_dir, "register_service_handler - Loading service json data...", task_id)
    import json
    with open(working_dir + '/service_conf/service.json') as data_file:
        data = json.load(data_file)

    log(working_dir, "register_service_handler - Add service to database...", task_id)
    from models import Application
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

    settings["INSTANCE_DOCKERS"] = data.get("dockers").replace(",","#")

    log(working_dir, "register_service_handler - Registering service in proxy", task_id)
    #REPLACE THE VALUES IN THE PROXY FILES
    copy_and_replace(working_dir + "/service_conf/proxy.upstream", settings.get("nginx_data_location") + instance_name + ".upstream", settings)
    copy_and_replace(working_dir + "/service_conf/proxy.conf", settings.get("nginx_data_location") + instance_name + ".conf", settings)

    log(working_dir, "register_service_handler - Add launcher file", task_id)
    command = "mkdir -p " + settings.get("ebiokit_data_location") + "ebiokit-services/launchers/" + instance_name
    output = subprocess.check_output(['bash', '-c', command])
    #REPLACE THE VALUES IN THE COMPOSE FILE
    copy_and_replace(working_dir + "/service_conf/service.launcher", settings.get("ebiokit_data_location") + "ebiokit-services/launchers/" + instance_name + "/docker-compose.yml", settings)

    log(working_dir, "register_service_handler - Add uninstall instructions", task_id)
    copy_and_replace(working_dir + "/service_conf/uninstall.json", settings.get("ebiokit_data_location") + "ebiokit-services/uninstallers/" + instance_name + ".json", settings)

    log(working_dir, "register_service_handler - Register ports", task_id)
    ports = get_service_ports(settings)
    n_rule = 1
    for port in ports:
        log(working_dir, "register_image_handler - Adding port forwarding rule for port " + port, task_id)
        command = "vboxmanage controlvm ebiokit natpf2 \"sp_" + instance_name + "_" + str(n_rule) + ",tcp,," + str(port) + ",," + str(port) + "\""
        output = subprocess.check_output(['bash', '-c', command])
        n_rule+=1
    return True

def register_vdi_image_handler(task_id, instance_name=None, settings=None):
    working_dir = get_job_directory(settings.get("tmp_dir"), task_id)

    log(working_dir, "register_image_handler - Get available SATA port", task_id)
    command = "VBoxManage showvminfo ebiokit | grep 'SATA (' | awk 'BEGIN{_next=0}{gsub(/\(|,/,\"\",$2); if(_next==$2){_next=_next+1;}}END{print _next;exit;}'"
    port = subprocess.check_output(['bash', '-c', command])
    port = int(port.rstrip())
    log(working_dir, "register_image_handler - Available SATA port: " + str(port), task_id)
    #TODO: REMOVE IF ALREADY THERE (SHOULD NOT BE THERE) -> FIND PORT AND SET TO NONE
    #print "Removing previous VDI (if any)"

    log(working_dir, "register_image_handler - Get new UUID for disk", task_id)
    command = "VBoxManage internalcommands sethduuid " + settings.get("ebiokit_data_location") + "ebiokit-data/" + instance_name + ".vdi"
    uuid = subprocess.check_output(['bash', '-c', command])
    import re
    uuid=re.compile(".*: ").sub("", uuid).rstrip()
    log(working_dir, "register_image_handler - New UUID for disk is: " + uuid, task_id)

    log(working_dir, "register_image_handler - Add init file", task_id)
    #REPLACE THE VALUES IN THE INIT FILE
    settings["UUID"] = uuid
    copy_and_replace(working_dir + "/service_conf/service.init", settings.get("ebiokit_data_location") + "ebiokit-services/init-scripts/" + instance_name + ".init", settings)

    stop_docker_machine_handler(task_id, settings)

    log(working_dir, "register_image_handler - Register new VDI in port " + str(port), task_id)
    command = "VBoxManage storageattach  ebiokit --storagectl SATA --port " + str(port) + " --device 0 --type hdd --medium " + settings.get("ebiokit_data_location") + "ebiokit-data/" + instance_name + ".vdi"
    output = subprocess.check_output(['bash', '-c', command])

    start_docker_machine_handler(task_id, settings)

    # log(working_dir, "register_image_handler - Obtaining drive UUID", task_id)
    # command = "VBoxManage showvminfo ebiokit | grep 'SATA (' | grep 'ebiokit-data/" + instance_name + ".vdi' | awk -F':' '{uuid=gsub(/ |)/,\"\",$3);print $3}'"
    # uuid = subprocess.check_output(['bash', '-c', command]).rstrip()
    # log(working_dir, "register_image_handler - Drive UUID is: " + uuid, task_id)
    return True

def prepare_upgrade_handler(task_id, instance_name=None, keep_data="keep", script_url=None, settings=None):
    working_dir = get_job_directory(settings.get("tmp_dir"), task_id)
    log(working_dir, "prepare_upgrade_handler - Running pre-upgrading scripts...", task_id)

    if keep_data == "keep" and osPath.isfile(settings.get("ebiokit_data_location") + "ebiokit-services/init-scripts/" + instance_name + ".init"):
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

    if keep_data == "keep" and osPath.isfile(working_dir + "/service.init_back"):
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

def start_docker_machine_handler(task_id, settings=None):
    working_dir = get_job_directory(settings.get("tmp_dir"), task_id)
    log(working_dir, "start_docker_machine_handler - Starting docker machine...", task_id)
    command = "startup"
    ebiokit_remote_launcher(command, settings)
    # TODO: DISABLE MAINTENANCE MODE

def stop_docker_machine_handler(task_id, settings=None):
    working_dir = get_job_directory(settings.get("tmp_dir"), task_id)
    log(working_dir, "restart_docker_machine_handler - Stopping docker machine...", task_id)
    command = "shutdown"
    ebiokit_remote_launcher(command, settings, ignore=True)
    #TODO: ENABLE MAINTENANCE MODE

def clean_data_handler(task_id, settings=None):
    #TODO docker_name param?
    working_dir = get_job_directory(settings.get("tmp_dir"), task_id)

    # if docker_name != None:
    #     print "Removing previous version for image " + docker_name + "..."
    #     command = "docker rmi ebiokit/" + docker_name + ":backup"
    #     ebiokit_remote_launcher(command, settings)

    log(working_dir, "clean_data_handler - Removing temporal data...", task_id)
    print
    from os import path
    if path.exists(working_dir):
        from shutil import rmtree
        rmtree(working_dir)
    return True

def uninstall_service_handler_part_1(task_id, instance_name=None, dockers="", settings=None):
    working_dir = get_job_directory(settings.get("tmp_dir"), task_id)

    #STEP 1. UNREGISTER THE  SERVICE (REMOVE FROM DB)
    log(working_dir, "uninstall_service_handler_part_1 - Removing service from database...", task_id)
    from models import Application
    service = Application.objects.get(instance_name=instance_name)
    service.delete()

    #STEP 2. STOP AND REMOVE DOCKER (CONTAINER? , IMAGE?)
    log(working_dir, "uninstall_service_handler_part_1 - Removing docker containers...", task_id)
    command = "docker-compose -f /ebiokit_services/launchers/" + instance_name + "/docker-compose.yml stop"
    ebiokit_remote_launcher(command, settings, ignore=True)

    command = "docker-compose -f /ebiokit_services/launchers/" + instance_name + "/docker-compose.yml rm -f"
    ebiokit_remote_launcher(command, settings, ignore=True)

    #TRY TO REMOVE DOCKER IMAGE
    log(working_dir, "uninstall_service_handler_part_1 - Removing docker images...", task_id)
    dockers = dockers.split("#")
    for docker in dockers:
        if docker != "":
            command = "docker rmi " + docker
            ebiokit_remote_launcher(command, settings, ignore=True)

    #STEP 5. UNREGISTER THE PORT FORWARDING RULES
    log(working_dir, "uninstall_service_handler_part_1 - Unregister the port forwarding rules in virtual machine...", task_id)
    command="vboxmanage showvminfo ebiokit --details | grep \"NIC 2\" | grep -oh \"sp_" + instance_name + "_[0-9]*,\" | tr -d '\n'"
    rules = subprocess.check_output(['bash', '-c', command])
    rules = rules.rstrip().rstrip(",").split(",")
    for rule in rules:
        command = "vboxmanage controlvm ebiokit natpf2 delete  \"" + rule + "\""
        output = subprocess.check_output(['bash', '-c', command])

    #STEP 6. REMOVE THE PROXY CONF
    if osPath.isfile(settings.get("nginx_data_location") + instance_name + ".upstream"):
        log(working_dir, "uninstall_service_handler_part_1 - Delete the NGINX UPSTREAM file...", task_id)
        osRemoveFile(settings.get("nginx_data_location") + instance_name + ".upstream")
    if osPath.isfile(settings.get("nginx_data_location") + instance_name + ".conf"):
        log(working_dir, "uninstall_service_handler_part_1 - Delete the NGINX CONF file...", task_id)
        osRemoveFile(settings.get("nginx_data_location") + instance_name + ".conf")

    #STEP 7. REMOVE THE LAUNCHER
    if osPath.isfile(settings.get("ebiokit_data_location") + "ebiokit-services/launchers/" + instance_name + "/docker-compose.yml"):
        log(working_dir, "uninstall_service_handler_part_1 - Delete the launcher file...", task_id)
        osRemoveFile(settings.get("ebiokit_data_location") + "ebiokit-services/launchers/" + instance_name + "/docker-compose.yml")
        osRemoveDir(settings.get("ebiokit_data_location") + "ebiokit-services/launchers/" + instance_name)

    #STEP 8. REMOVE THE UNINSTALLER
    if osPath.isfile(settings.get("ebiokit_data_location") + "ebiokit-services/uninstallers/" + instance_name + ".json"):
        log(working_dir, "uninstall_service_handler_part_1 - Delete the uninstaller file...", task_id)
        osRemoveFile(settings.get("ebiokit_data_location") + "ebiokit-services/uninstallers/" + instance_name + ".json")


def uninstall_service_handler_part_2_vdi(task_id, instance_name=None, dockers="", settings=None):
    working_dir = get_job_directory(settings.get("tmp_dir"), task_id)

    #STEP 9. STOP THE VIRTUAL MACHINE
    stop_docker_machine_handler(task_id,settings)

    #STEP 10. UNREGISTER THE VDI IMAGE IN VIRTUAL MACHINE
    log(working_dir, "uninstall_service_handler_part_2_vdi - Unregister the VDI image in virtual machine...", task_id)
    command = "VBoxManage showvminfo ebiokit | grep 'SATA (' | grep '" + instance_name + ".vdi' | awk '{gsub(/\(|,/,\"\",$2); print $2}'"
    port = subprocess.check_output(['bash', '-c', command])
    port = port.rstrip()
    command = "VBoxManage showvminfo ebiokit | grep 'SATA (' | grep '" + instance_name + ".vdi' | sed 's/.*UUID: //' | sed 's/)$//'"
    uuid = subprocess.check_output(['bash', '-c', command])
    uuid = uuid.rstrip()

    command = "vboxmanage storageattach ebiokit --storagectl \"SATA\" --port " + port + " --medium none"
    output = subprocess.check_output(['bash', '-c', command])

    #STEP 11. REMOVE THE INIT FILE
    if osPath.isfile(settings.get("ebiokit_data_location") + "ebiokit-services/init-scripts/" + instance_name + ".init"):
        log(working_dir, "uninstall_service_handler_part_2_vdi - Delete the INIT file...", task_id)
        osRemoveFile(settings.get("ebiokit_data_location") + "ebiokit-services/init-scripts/" + instance_name + ".init")

    #STEP 12. RELAUNCH DOCKER MACHINE
    start_docker_machine_handler(task_id,settings)

    #STEP 13. REMOVE THE VDI FILE
    if osPath.isfile(settings.get("ebiokit_data_location") + "ebiokit-data/" + instance_name + ".vdi"):
        log(working_dir, "uninstall_service_handler_part_2_vdi - Delete the VDI image...", task_id)
        osRemoveFile(settings.get("ebiokit_data_location") + "ebiokit-data/" + instance_name + ".vdi")

    command = "vboxmanage closemedium disk " + uuid
    output = subprocess.check_output(['bash', '-c', command])

def uninstall_service_handler_part_2_commondata(task_id, instance_name=None, dockers="", settings=None):
    working_dir = get_job_directory(settings.get("tmp_dir"), task_id)

    #STEP 9. REMOVE THE DATA DIRECTORY
    log(working_dir, "uninstall_service_handler_part_2_commondata - Removing application data...", task_id)
    command = "sudo /home/ebiokit/rmdatadir /data/common-data/" + instance_name + "-data/"
    ebiokit_remote_launcher(command, settings, ignore=True)

def get_job_directory(tmp_dir, task_id, settings=None):
    jobID = task_id.split("_")[0]
    from os import path, makedirs
    wd = path.join(tmp_dir, jobID)
    if not path.exists(wd):
        makedirs(wd)
    return wd

def copy_and_replace(source_file, target_file, replacements):
    source_file = open(source_file, 'r')
    target_file = open(target_file, 'w')
    for line in source_file:
        for key, value in replacements.iteritems():
            line = line.replace("$${" + key + "}", str(value))
        target_file.write(line)
    source_file.close()
    target_file.close()

def log(working_dir, message, task_id=""):
    print task_id + " - " + message
    if working_dir != None:
        log_file = open(working_dir + "/" + task_id + ".log", 'a')
        log_file.write(task_id + " - " + message + "\n")
        log_file.close()

def ebiokit_remote_launcher(command, settings=None, ignore=False):
    command = osPath.join(osPath.dirname(osPath.realpath(__file__)), '../admin_tools/ebiokit_launcher.sh') + ' "' + settings.get("ebiokit_host") + '" "'  + settings.get("ebiokit_password") + '" "'  + settings.get("platform") + '" "' + command + '"'
    try:
        output = subprocess.check_output(['bash', '-c', command])
    except Exception as ex:
        if ignore == True:
            pass
        else:
            raise ex

    return True

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
