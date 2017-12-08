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

from rest_framework import serializers
from applications.models import Application, RemoteServer, Job, Task, Settings, User

class ApplicationSerializer(serializers.ModelSerializer):
    """ Serializer to represent the Application model """
    class Meta:
        model = Application
        fields = ("instance_name", "service", "version", "title", "description", "categories", "website", "port", "type", "installed", "enabled")

class RemoteServerSerializer(serializers.ModelSerializer):
    """ Serializer to represent the RemoteServer model """
    class Meta:
        model = RemoteServer
        fields = ("name", "url", "enabled")

class JobSerializer(serializers.ModelSerializer):
    """ Serializer to represent the RemoteServer model """
    class Meta:
        model = RemoteServer
        fields = ("id", "name", "date")

class TaskSerializer(serializers.ModelSerializer):
    """ Serializer to represent the RemoteServer model """
    class Meta:
        model = RemoteServer
        fields = ("job_id", "id", "name", "command", "status")

class SettingsSerializer(serializers.ModelSerializer):
    """ Serializer to represent the Settings model """
    class Meta:
        model = Settings
        fields = ("name", "value")

class UserSerializer(serializers.ModelSerializer):
    """ Serializer to represent the User model """
    class Meta:
        model = User
        fields = ("name", "email", "password", "role")