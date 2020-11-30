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
import logging

from django.http import JsonResponse
from rest_framework import viewsets, renderers
from rest_framework.decorators import action

from .models import User
from .resources.UserSessionManager import UserSessionManager

# Get an instance of a logger
logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    """ This file contains all the functions for managing the API requests related with users """

    # ----------------------------------------------------------------------------------------------
    #    _  _    _    _  _  ___   _     ___  ___  ___
    #   | || |  /_\  | \| ||   \ | |   | __|| _ \/ __|
    #   | __ | / _ \ | .` || |) || |__ | _| |   /\__ \
    #   |_||_|/_/ \_\|_|\_||___/ |____||___||_|_\|___/
    # --------------------------------------------------------------------------------------------

    @action(detail=True, renderer_classes=[renderers.JSONRenderer])
    def get_user(self, request):
        return JsonResponse({'success': False, 'error_message': 'Not implemented"'})

    @action(detail=True, renderer_classes=[renderers.JSONRenderer])
    def create_user(self, request):
        try:
            user = User()
            user.name = request.data.get("username")
            user.email = request.data.get("email")
            user.password = request.data.get("password")
            user.role = "guest"
            user.save()
            return JsonResponse({'success': True})
        except Exception as ex:
            return JsonResponse({'success': False, 'other': {'error_message': ex.message}})

    @action(detail=True, renderer_classes=[renderers.JSONRenderer])
    def update_user(self, request):
        return JsonResponse({'success': False, 'error_message': 'Not implemented"'})

    @action(detail=True, renderer_classes=[renderers.JSONRenderer])
    def validate_session(self, request):
        try:
            # STEP 0. CHECK IF USER IS VALID
            UserSessionManager().validate_session(request.COOKIES.get('ebiokitsession'))
            return JsonResponse({'success': True})
        except Exception as ex:
            return JsonResponse({'success': False, 'other': {'error_message': ex.message}})

    @action(detail=True, renderer_classes=[renderers.JSONRenderer])
    def sign_in(self, request):
        import base64
        info = base64.b64decode(request.data.get("token"))
        info = info.split(":", 1)

        try:
            user = User.objects.get(email=info[0], password=info[1])
            session_token = UserSessionManager().open_session(user.email, user.role)
            return JsonResponse({'success': True, 'session_token': session_token})
        except:
            response = JsonResponse({'success': False, 'err_code': 404001})
            response.status_code = 500
            return response

    @action(detail=True, renderer_classes=[renderers.JSONRenderer])
    def sign_out(self, request):
        try:
            # STEP 0. CHECK IF USER IS VALID
            if request.COOKIES.get('ebiokitsession') != None:
                UserSessionManager().close_session(request.COOKIES.get('ebiokitsession'))
            return JsonResponse({'success': True})
        except Exception as ex:
            return JsonResponse({'success': False, 'other': {'error_message': ex.message}})
