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
from google.appengine.ext import deferred

from controllers import sites

from modules.um_common.handlers import UMBaseHandler

from .service import deferred_send_badges


class SendBadgesHandler(UMBaseHandler):
    """ Unused handler

        This handler allows to create a process to issue
        all SentBadge with status PENDING in db
    """

    def get_public_courses(self):
        """Get all the public courses."""
        public_courses = []
        for course in sites.get_all_courses():
            info = sites.ApplicationContext.get_environ(course)
            if info['course']['now_available']:
                public_courses.append(course)
        return public_courses

    def get_course_yaml(self, course):
        """ Get the configurations for a course """
        course_info = sites.ApplicationContext.get_environ(course)
        course_info[
            '_namespace'] = sites.ApplicationContext.get_namespace_name(course)
        return course_info

    def process_badges(self):
        """ Iterate over courses and issue badges pending """
        configurations = []
        for course in self.get_public_courses():
            configurations.append(self.get_course_yaml(course))
        deferred.defer(deferred_send_badges, configurations)

    def post(self):
        self.process_badges()

    def get(self):
        self.process_badges()
