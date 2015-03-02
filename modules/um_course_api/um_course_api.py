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

""" Course API module
    This module offers a number of URL endpoints with which
    you are able to GET, POST, PUT and DELETE all the content
    of a course. There are other methods available in other
    modules, but these are easier and simpler to use.
"""


from models import custom_modules

from modules.um_course_api import handlers


def register_module():
    """Registers this module in the registry."""

    global_urls = [
        ('/api/courses', handlers.CoursesAPIHandler),
        ('/api/courses/(.*)', handlers.CoursesAPIHandler),
        ('/api/courses/(.*)/units', handlers.UnitsAPIHandler),
        ('/api/courses/(.*)/units/(.*)', handlers.UnitsAPIHandler)
    ]

    course_urls = []

    global custom_module
    custom_module = custom_modules.Module(
        'Course API',
        'A set of URL endpoints to access all the course data.',
        global_urls, course_urls)
    return custom_module
