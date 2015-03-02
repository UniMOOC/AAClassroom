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

from models.models import Student
from models.models import StudentProfileDAO

from modules.um_gobalo.service import GobaloAPI
from .exceptions import UserNotAuthorized


class Students(object):

    @classmethod
    def get_by_email(cls, student_email):
        return Student.get_by_email(cls._plain_email(student_email))

    @classmethod
    def register_user(cls, user):
        from modules.um_editions.service import Editions

        student = Student.get_enrolled_student_by_email(user.email())
        if student:
            return student

        name, last_name, edition_code = GobaloAPI.get_user_info(user.email())

        if not name:
            raise UserNotAuthorized('gobalo_user_not_authorized')
        if not Editions.get(edition_code):
            raise UserNotAuthorized('edition_for_student_not_exists')

        additional_fields = json.dumps({
            'name': name, 'last_name': last_name, 'edition_code': edition_code,
            'original_email': user.email(), 'acreditations_email': user.email()
        })

        student = StudentProfileDAO._add_new_student_for_current_user(
            user.user_id(),
            cls._plain_email(user.email()),
            name + ' ' + last_name,
            additional_fields
        )

        Editions.register_user(edition_code, student)
        return student

    @classmethod
    def _plain_email(cls, email):
        user_mail, domain_mail = email.lower().split("@")
        plain_email = user_mail.replace(".", "") + "@" + domain_mail
        return plain_email

    @classmethod
    def clean_email(cls, email):
        return cls._plain_email(email)
