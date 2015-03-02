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

""" Courses module
    This module overrides several URLs of the base GCB and puts our
    own in their place.
"""

from models import custom_modules

from modules.um_course import handlers


def register_module():
    """Registers this module in the registry."""

    global_urls = []

    course_urls = [
        ('/', handlers.CourseHandler),
        ('/course', handlers.CourseHandler),
        ('/api/register', handlers.RegisterAPIHandler),
        ('/api/course', handlers.CourseAPIHandler),
        ('/api/course/info', handlers.CourseInfoAPIHandler),
        ('/api/student/progress', handlers.ProgressAPIHandler),
        ('/api/offline-load', handlers.LoadOfflineCourseAPIHandler),
        ('/api/offline-data', handlers.LoadOfflineCourseDataAPIHandler)
    ]

    global custom_module
    custom_module = custom_modules.Module(
        'UM Course',
        'Rewrite of some of the GCB routes',
        global_urls, course_urls)

    return custom_module
