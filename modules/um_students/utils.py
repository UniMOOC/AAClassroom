# Copyright 2015 UniMOOC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

from oauth2client import crypt
from oauth2client.crypt import AppIdentityError

from models.models import MemcacheManager

from modules.um_common.tools import UrlfetchHelper
from modules.um_common.utils import FakeUser
from modules.um_common.utils import ConfigReader
from .service import Students
from .exceptions import UserNotAuthorized


CONFIG = ConfigReader('modules/um_common/config.yaml')


class AuthenticationService(object):

    GOOGLE_CERTS_MEMCACHE = 'authentication-google-certs'

    @classmethod
    def um_verify_id_token(cls, id_token):
        # Client library can verify the ID token.
        audience = CONFIG['google_api_key']
        certs = cls.google_certs()
        if certs:
            try:
                jwt = crypt.verify_signed_jwt_with_certs(
                    id_token, certs, audience)
                return jwt
            except AppIdentityError:
                cls.refresh_certs()
                raise
        else:
            raise Exception("Can't get google certs")

    @classmethod
    def google_certs(cls):
        certs = MemcacheManager.get(cls.GOOGLE_CERTS_MEMCACHE)
        if not certs:
            certs = cls.refresh_certs()
        return certs

    @classmethod
    def refresh_certs(cls):
        uri = 'https://www.googleapis.com/oauth2/v1/certs'
        resp = UrlfetchHelper.get_simple(uri)
        if resp.status_code == 200:
            certs = json.loads(resp.content)
            MemcacheManager.set(cls.GOOGLE_CERTS_MEMCACHE, certs)
            return certs
        else:
            raise Exception("Google api certs uri is not available")


def gpluslogin(fn):
    """ Decorator to inject a student by their Google id token
    """
    def inner_fn(handler, *args, **kwargs):
        try:
            id_token = handler.request.headers.get('Id-Token')
            if not id_token:
                return handler.return_with_error(
                    401, 'Id-Token header is required')
            jwt = AuthenticationService.um_verify_id_token(id_token)

            if not jwt:
                return handler.return_with_error(
                    401, 'Id-Token not valid')

            email = jwt['email']
            student = Students.get_by_email(email)

            if not student:
                try:
                    user = FakeUser(email, jwt['sub'])
                    student = Students.register_user(user)
                    if not student:
                        raise UserNotAuthorized(
                            'User not authorized or edition does not exist')

                except UserNotAuthorized as e:
                    return handler.return_with_error(403, str(e))

            from modules.um_course.service import Courses
            student.is_admin = Courses.is_course_admin(
                student.original_email()
            )

            handler.student = student

        except AppIdentityError as ex:
            import logging
            logging.error(str(ex))
            return handler.return_with_error(
                401, 'API Identity error')

        return fn(handler, *args, **kwargs)
    return inner_fn
