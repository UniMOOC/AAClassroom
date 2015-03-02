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

""" Student module
    This module has all functions related with an student.
    It includes an api to get data, exceptions, utils and
    services to get or change student data.
"""


from models import custom_modules
from models.models import Student

from modules.um_common.utils import mix_in
from modules.um_students.mixin import StudentMixin
from .handlers import StudentAPIHandler
from .handlers import StudentAttemptsAPIHandler


def register_module():
    """Registers this module in the registry."""

    mix_in(Student, StudentMixin)

    global_urls = [
    ]

    course_urls = [
        ('/api/student', StudentAPIHandler),
        ('/api/student/attempts_needed', StudentAttemptsAPIHandler)
    ]

    global custom_module
    custom_module = custom_modules.Module(
        'Module Student',
        'Module to expose and manage students',
        global_urls, course_urls)
    return custom_module
