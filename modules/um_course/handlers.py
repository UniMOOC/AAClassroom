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
# encoding=utf-8

import os
import datetime
import appengine_config

from models.vfs import FileDataEntity

from modules.um_common.utils import is_super_admin
from modules.um_common.utils import ConfigReader
from modules.um_common.utils import TimeHelper
from modules.um_common.handlers import UMBaseHandler
from modules.um_students.utils import gpluslogin
from modules.um_course.service import Courses
from modules.um_editions.service import Editions
from modules.um_assessments.service import AsmDates
from modules.um_badges.service import OpenBadges


VIEWS_DIR = os.path.normpath(os.path.dirname(__file__)) + '/views'

CONFIG = ConfigReader('modules/um_course/config.yaml')


class CourseHandler(UMBaseHandler):
    """ Handlers for /course and / """

    def get(self):
        """ Loads the course HTML file with has the main AngularJS app"""
        self.template_value['navbar'] = {'course': True}

        self.render('course.html', VIEWS_DIR)


class CourseAPIHandler(UMBaseHandler):
    """ Handlers for /api/course"""

    @gpluslogin
    def get(self):
        """ Retrieves the info of the course

            Returns:
            A json list with the info of each and every unit of the course.
        """
        units = Courses.get_units()

        edition = Editions.get_edition_of_student(self.student)

        dates = AsmDates.get_by_edition(edition)
        self.student.cert_email = self.student.get_field(
            'acreditations_email'
        )
        for unit in units:
            if unit['type'] == 'A' or unit['type'] == 'F':
                unit['badge'] = OpenBadges.create_badge_url(
                    unit['badge'], self.student.cert_email)
                if unit['type'] == 'F':
                    # TODO: Hacer esto bien, ponerle un campo al examen y tal
                    unit['certificate'] = OpenBadges.create_certificate_url(
                        'mkd-esp-final', self.student.cert_email,
                        check_badge=True
                    )
                for date in dates:
                    if date.assessment == str(unit['unit_id']):
                        unit_dates = unit.get('dates', [])
                        start_date = TimeHelper.to_GMT1(date.start_date)
                        end_date = TimeHelper.to_GMT1(date.end_date)
                        unit_dates.append({
                            'start_date': start_date.isoformat(),
                            'end_date': end_date.isoformat(),
                            'attempts': date.attempts
                        })
                        unit['dates'] = unit_dates
            elif unit['type'] == 'U':
                unit['certificate'] = OpenBadges.create_certificate_url(
                    str(unit['certificate']), self.student.cert_email,
                    check_badge=True
                )
        course_info = Courses.get_course_settings()
        course_info['edition_name'] = edition
        course_info['units'] = units

        self.write_json(course_info)


class RegisterAPIHandler(UMBaseHandler):
    """ Handlers for /api/register"""

    @gpluslogin
    def post(self):
        """ Makes sure the user is "logged in"

            Does nothing really. It's used by the frontend app to make sure a
            user is allowed inside the app. Registers the user if it's a new
            student as a side effect.
        """
        try:
            self.student.check_today_attended()
        except:
            pass
        self.write_json({
            'is_admin': self.student.is_admin,
            'name': self.student.complete_name()
        })


class ProgressAPIHandler(UMBaseHandler):
    """ Handlers for /api/progress"""

    @gpluslogin
    def get(self):
        """ Retrieves the progress of a student

            Returns the progress of the authenticated student
        """
        progress = self.student.get_course_progress()
        self.write_json(progress)


class CourseInfoAPIHandler(UMBaseHandler):
    """ Handlers for /api/course/info"""

    @is_super_admin
    def get(self):
        units = Courses.get_units()
        dict_units = {}
        for unit in units:
            dict_units[unit['unit_id']] = unit['title']
        self.write_json(dict_units)


class LoadOfflineCourseDataAPIHandler(UMBaseHandler):
    """ Handlers for /api/offline-data """

    @is_super_admin
    def get(self):
        course = FileDataEntity.get_by_key_name("/data/course.json")
        self.response.out.write(course.data)


class LoadOfflineCourseAPIHandler(UMBaseHandler):
    """ Handlers for /api/offline-load """

    @is_super_admin
    def get(self):
        from google.appengine.api import app_identity
        self.response.write(
            '<form action="offline-load" method="POST">' +
            '<button type="submit" onclick="return confirm(\'Seguro?\')">' +
            'Extremly danger >></button></form>' +
            app_identity.get_application_id())

    @is_super_admin
    def post(self):
        """ Loads a course from data/course.json

        Not meant to be used in production enviroments, only in development.
        """

        if not appengine_config.PRODUCTION_MODE:
            course = FileDataEntity.get_by_key_name("/data/course.json")

            course.data = open('data/course_basic.json', 'r').read()

            course.put()

            start_date = datetime.datetime.now()
            Editions.create_edition('md-bas-madrid-03', start_date)
        else:
            course = FileDataEntity.get_by_key_name("/data/course.json")
            self.response.out.write(course.data)
