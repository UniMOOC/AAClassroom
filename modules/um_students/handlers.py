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

from modules.um_badges.service import Badges
from modules.um_certificates.service import AssessmentCertificates
from modules.um_assessments.service import AsmAttempts
from modules.um_assessments.service import AsmDates
from modules.um_editions.service import Editions
from modules.um_students.service import Students

from modules.um_common.handlers import UMBaseHandler
from modules.um_course_api.handlers import BaseAPIHandler
from modules.um_course_api.exceptions import NotFoundException
from .service import Students
from .model import StudentAPISerializer


USER_404 = 'User {} not found'
BADGE_404 = 'Badge {} not found'
NOT_AWARDED_404 = "User {} doesn't have badge {}."
NO_EDITION_404 = "User {} is not in any edition."
DATES_500 = "Database inconsistency in the assessment dates table"


class StudentAPIHandler(BaseAPIHandler):
    _ALLOWED_METHODS = ['GET', 'POST']
    _ID_KEYS = ['email']

    def retrieve(self):
        user = self._get_user()
        self.write_json(StudentAPISerializer(user))

    def post(self):
        user = self._get_user()
        user_requested = StudentAPISerializer(json.loads(self.request.body))
        user = user_requested.to_student(user)
        user.put()
        self.write_json(StudentAPISerializer(user))

    def list(self):
        pass

    def _get_user(self):
        user = Students.get_by_email(self.param('email', True))
        if not user:
            raise NotFoundException(
                'User ' + self.param('email') + ' not found')
        return user


class StudentAttemptsAPIHandler(UMBaseHandler):

    def get(self):
        email = self._process_email(self.request.get('email'))
        atts = AsmAttempts.get(email)
        if not atts:
            self.return_with_error(404, USER_404.format(email))
            return

        badge_id = self.request.get('badge')
        badges = AssessmentCertificates.get_by_id(badge_id)
        if not badges:
            self.return_with_error(404, BADGE_404.format(badge_id))
            return

        badge = badges[0]

        if not Badges.student_has_badge(email, badge_id):
            self.return_with_error(
                404, NOT_AWARDED_404.format(email, badge_id)
            )
            return

        asm_id = badge.assessments[0]

        student = Students.get_by_email(email)
        editions = student.get_field('editions', [])
        if not editions:
            self.return_with_error(404, NO_EDITION_404.format(email))
            return
        edition = editions[0]

        asm_dates = AsmDates.get(edition, asm_id)
        if not asm_dates:
            self.return_with_error(500, DATES_500)
            return

        total_atts = sum((d.attempts for d in asm_dates))
        atts_left = sum((atts.attempts_left[str(d.id)] for d in asm_dates))

        self.response.status = 200
        self.response.out.write(total_atts - atts_left)

    def _process_email(self, email):
        name, domain = email.split('@')
        name = name.lower().replace('.', '')
        return '{}@{}'.format(name, domain)
