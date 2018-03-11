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

import base64
from django.conf import settings
from ..models import User
from ..serializers import UserSerializer

class UserSessionManager(object):

    #Implementation of the singleton interface
    class __impl:

        def open_session(self, user_id, role):
            import string
            import random
            user_id = str(user_id)
            sessionToken =''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(50))
            user = User.objects.get(email=user_id)
            user.session_id = sessionToken
            user.save()
            return sessionToken

        def close_session(self, sessionToken):
            sessionToken = base64.b64decode(sessionToken.replace("%3D", "="))
            user_id = sessionToken.split(":", 1)[0]
            sessionToken = sessionToken.split(":", 1)[1]
            try:
                user = User.objects.get(email=user_id, session_id=sessionToken)
                if (user != None):
                    user.session_id = ""
                    user.save()
                    return True
            except:
                pass
            return False

        def validate_session(self, sessionToken):
            DEBUG_MODE = (getattr(settings, "DEBUG", None) is True)
            sessionToken = base64.b64decode(sessionToken.replace("%3D", "="))
            user_id = sessionToken.split(":", 1)[0]
            sessionToken = sessionToken.split(":", 1)[1]
            if not DEBUG_MODE and (user_id == 'None' or sessionToken == None or sessionToken == ""):
                raise CredentialException("[b]User not valid[/b]. It looks like your session is not valid, please log-in again.")
            try:
                user = User.objects.get(email=user_id, session_id=sessionToken)
            except:
                user = None
            if not DEBUG_MODE and user == None:
                raise CredentialException("[b]User not valid[/b]. It looks like your session is not valid, please log-in again.")
            return user_id

        def validate_admin_session(self, sessionToken):
            DEBUG_MODE = (getattr(settings, "DEBUG", None) is True)
            user_id = self.validate_session(sessionToken)
            user = User.objects.get(email=user_id)
            if not DEBUG_MODE and not(user.role in ["admin", "superuser"]):
                raise CredentialException("[b]User not valid[/b]. Your user is not a valid administrator for this machine.")
            return user_id

    # storage for the instance reference
    __instance = None

    def __init__(self):
        """ Create singleton instance """
        # Check whether we already have an instance
        if UserSessionManager.__instance is None:
            # Create and remember instance
            UserSessionManager.__instance = UserSessionManager.__impl()

        # Store instance reference as the only member in the handle
        self.__dict__['_UserSessionManager__instance'] = UserSessionManager.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)

class CredentialException(Exception):
    pass
