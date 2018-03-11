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

from django.db import models
from django.utils import timezone

#If new model is created, run this functions:
# python manage.py makemigrations
# python manage.py migrate

class Application(models.Model):
    """ High-level application model"""
    instance_name = models.CharField(max_length=100, unique=True)
    service = models.CharField(max_length=100)
    version = models.CharField(max_length=100, default="0.1")
    title = models.CharField(max_length=100, default="New application")
    description = models.CharField(max_length=1000)
    categories = models.CharField(max_length=500)
    website = models.CharField(max_length=500)
    port = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=1, default="1")
    installed = models.DateTimeField(default=timezone.now)
    enabled = models.BooleanField(default=1)
    raw_options = models.CharField(max_length=2000, default="")

class RemoteServer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    url = models.CharField(max_length=300)
    enabled = models.BooleanField(default=0)

class Job(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=300)
    date = models.CharField(max_length=12)

class Task(models.Model):
    job_id = models.CharField(max_length=100)
    id = models.CharField(max_length=300, primary_key=True)
    name = models.CharField(max_length=300)
    command = models.TextField(default="")
    function = models.TextField(default="")
    params = models.TextField(default="")
    depend = models.TextField(default="")
    incompatible = models.TextField(default="")
    status = models.CharField(max_length=100)

class Settings(models.Model):
    name = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=300)

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=20)
    session_id = models.CharField(max_length=100, default="")


