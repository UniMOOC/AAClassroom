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

from controllers import sites
from models.courses import Course
from models.roles import Roles

from modules.um_common.utils import FakeUser


class Courses(object):

    @classmethod
    def get_course_title(cls):
        return cls.get_course().title

    @classmethod
    def get_assessments(cls):
        return cls.get_course().get_units_of_type('A')

    @classmethod
    def get_course(cls):
        return Course.get(cls._app_context())

    @classmethod
    def is_course_admin(cls, email):
        return Roles.is_course_admin(
            sites.get_course_for_current_request(),
            _user=FakeUser(email, None)
        )

    @classmethod
    def find_unit_by_id(cls, unit_id):
        return cls.get_course().find_unit_by_id(unit_id)

    @classmethod
    def get_units(cls):
        return [cls._unit_to_dict(unit)
                for unit in cls.get_course().get_units()]

    @classmethod
    def get_course_settings(cls):
        return cls._app_context().get_environ().get('course', {})

    @classmethod
    def _app_context(cls):
        return sites.get_course_for_current_request()

    @classmethod
    def _unit_to_dict(cls, unit):
        if unit.type == 'A':
            return cls._asm_to_dict(unit)
        else:
            return {
                'type': unit.type,
                'unit_id': unit.unit_id,
                'title': unit.title,
                'certificate': unit.certificate,
                'docs': unit.docs
            }

    @classmethod
    def _asm_to_dict(cls, unit):
        return {
            'type': 'A' if not unit.required_asms else 'F',
            'unit_id': unit.unit_id,
            'title': unit.title,
            'unit_image': unit.unit_image,
            'unit_parent': unit.unit_parent,
            'min_score': unit.min_score,
            'docs': unit.docs,
            'badge': unit.badge,
            'required_asms': unit.required_asms.split(',')
            if unit.required_asms else []
        }
