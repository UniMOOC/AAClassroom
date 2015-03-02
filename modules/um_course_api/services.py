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

""" Classes used as proxy to access course data """


from .exceptions import NotFoundException

from .serializers import CourseSerializer
from .api_models import Course

COURSES = {
    'chuli': Course('chuli', 'Curso chuli')
}


class CourseAPI(object):

    @classmethod
    def get_course(cls, key):
        try:
            return CourseSerializer.serialize(COURSES[key])
        except KeyError:
            raise NotFoundException()

    @classmethod
    def get_courses(cls):
        return [CourseSerializer.serialize(course)
                for key, course in COURSES.iteritems()]
