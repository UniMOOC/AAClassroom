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

import json

from modules.um_common.handlers import UMBaseHandler
from modules.um_certificates.service import AssessmentCertificates
from modules.um_students.utils import gpluslogin
from modules.um_editions.service import Editions
from modules.um_course_api.handlers import BaseAPIHandler
from modules.um_students.service import Students
from modules.um_common.utils import is_super_admin

from .service import Assessments
from .service import AsmDates
from .service import AsmAttempts
from .service import ExtraAttempts
from .exceptions import NoAttemptsLeft
from .exceptions import NoDatesAvailable
from modules.um_students.exceptions import NoClassAttendance
from modules.um_students.exceptions import TooManyMissedDays
from .model import AsmDateModel, AsmDateDTO, AsmAttemptsModel,\
    AsmAttemptsDTO, AsmDateDAO


class AsmAPIHandler(UMBaseHandler):
    """ Handlers for the route /api/assessment """

    @gpluslogin
    def get(self):
        """ Returns the questions of an assessment

            Receives a {unit_id} corresponding to an assessment and returns the
            questions of that assessment.

            GET Parameters:
            - unit_id: the id of the assessment to be graded

            Returns:
            A json of the assessment with all of its parameters.
        """
        asm = self._get_asm_from_request()

        try:
            self._check_attendance(self.student, asm.unit_id)
            self._check_attempts(self.student, asm.unit_id)
        except NoAttemptsLeft:
            return self.return_with_error(403, 'no_attempts_left')
        except NoDatesAvailable:
            return self.return_with_error(403, 'no_dates_available')
        except NoClassAttendance:
            return self.return_with_error(403, 'no_class_attendance')
        except TooManyMissedDays:
            return self.return_with_error(403, 'too_many_missed_days')

        asm = self._assessment_transformer(asm)

        self.write_json(asm)

    @gpluslogin
    def post(self):
        """ Receives the answers of an assessment and grades it

            Receives a {unit_id} and an {answers} dict and proceeds to grade
            those answers for that assessment.

            POST Parameters:
            - unit_id: the id of the assessment to be graded
            - answers: a json dict like {'01': 2, '02':2} with the id of each
                question as a key and the answer for that question as value.

            Returns:
            A json with the score and some extra info
        """
        asm = self._get_asm_from_request()

        try:
            self._check_attendance(self.student, asm.unit_id)
            self._check_attempts(self.student, asm.unit_id, decrease=True)
        except NoAttemptsLeft:
            return self.return_with_error(403, 'no_attempts_left')
        except NoDatesAvailable:
            return self.return_with_error(403, 'no_dates_available')
        except NoClassAttendance:
            return self.return_with_error(403, 'no_class_attendance')
        except TooManyMissedDays:
            return self.return_with_error(403, 'too_many_missed_days')

        answers = json.loads(self.request.get('answers') or '{}')
        score, feedback = Assessments.grade_and_update_score(
            asm.html_content, answers, self.student, asm.unit_id)

        badges_issued =\
            AssessmentCertificates.issue_certificates_by_assessment(
                self.student, asm.unit_id, self.edition_key)

        response = {
            'score': score,
            'badge': [b for b in badges_issued if 'asist' not in b],
            'feedback': feedback
        }

        self.write_json(response)

    def _strip_answers(self, questions):
        for question in questions:
            if 'correct' in question:
                del question['correct']
        return questions

    def _get_asm_from_request(self):
        unit_id = self.request.get('unit_id')
        if not unit_id:
            self.abort(400)
        asm = Assessments.find_unit_by_id(unit_id)
        asm.unit_id = str(asm.unit_id)
        return asm

    def _check_attendance(self, student, asm_id):
        self.edition_key = Editions.get_edition_of_student(self.student)
        if self.student.is_admin:
            return
        asm_date = AsmDates.get_todays(self.edition_key, asm_id)
        if asm_date and asm_date.check_attendance:
            student.check_today_attended()

    def _check_attempts(self, student, asm_id, decrease=False):
        if self.student.is_admin:
            return
        edition_key = Editions.get_edition_of_student(self.student)
        AsmAttempts.check_attempts(student, edition_key, str(asm_id), decrease)

    def _assessment_transformer(self, assessment):
        assessment.html_content = self._strip_answers(assessment.html_content)
        send_response = {
            'title': assessment.title,
            'unit_id': assessment.unit_id,
            'min_score': assessment.min_score,
            'questions': assessment.html_content
        }
        assessment.html_content = self._strip_answers(assessment.html_content)
        return send_response


class AsmDatesAPIHandler(BaseAPIHandler):
    """ Handlers for the route /api/assessment/dates """
    _MODEL_HANDLER = AsmDateModel
    _DTO_HANDLER = AsmDateDTO
    _ID_KEYS = ['id']
    _FILTER_KEYS = ['edition']

    def update(self, model):
        old_attempts = model.attempts
        new_attemps = self._request_to_model().attempts
        super(AsmDatesAPIHandler, self).update(model)
        if old_attempts != new_attemps:
            attempts_difference = new_attemps - old_attempts
            self._update_students_attemps(
                attempts_difference,
                model.edition,
                model.key().id())

    def _update_students_attemps(self, difference, edition_id, asm_date_id):
        edition = Editions.get(edition_id)
        for user in edition.users:
            asm_attempts = AsmAttempts.get(user)
            for key in asm_attempts.attempts_left:
                if int(key) == asm_date_id:
                    asm_attempts.attempts_left[key] += difference
                    if asm_attempts.attempts_left[key] < 0:
                        asm_attempts.attempts_left[key] = 0
                    AsmAttempts.set(asm_attempts)
                    break


class AsmDatesBulkAPIHandler(BaseAPIHandler):
    _ALLOWED_METHODS = ['POST']
    """ Handlers for the route /api/assessment/dates/_bulk """
    @is_super_admin
    def post(self):
        dates = json.loads(self.request.body)
        for date in dates:
            old_date = AsmDateModel.get_by_id(date['id'])
            if old_date:
                for p_model, p_type in AsmDateModel._properties.items():
                    attr = self._parse_property(
                        date.get(p_model, None), p_type.data_type)
                    if attr is not None:
                        setattr(old_date, p_model, attr)
                old_date.put()


class ExtraAttemptAPIHandler(AsmAPIHandler):
    @gpluslogin
    def get(self):
        asm = self._get_asm_from_request()
        asm = self._assessment_transformer(asm)

        self.write_json(asm)

    @gpluslogin
    def post(self):
        asm = self._get_asm_from_request()

        answers = json.loads(self.request.get('answers') or '{}')
        score, feedback = Assessments.grade_and_update_score(
            asm.html_content, answers, self.student, asm.unit_id)

        edition_key = Editions.get_edition_of_student(self.student)

        badges_issued =\
            AssessmentCertificates.issue_certificates_by_assessment(
                self.student, asm.unit_id, edition_key)

        ExtraAttempts.remove_extra_attempt(self.student.email, asm.unit_id)

        response = {
            'score': score,
            'badge': [b for b in badges_issued if 'asist' not in b],
            'feedback': feedback
        }

        self.write_json(response)

    def _get_asm_from_request(self):
        url_hash = self.request.get('url_hash')
        asm_id = ExtraAttempts.unhash(self.student.email, url_hash)
        asm = Assessments.find_unit_by_id(asm_id)
        asm.unit_id = str(asm.unit_id)
        return asm


class StudentExtraAttemptAPIHandler(UMBaseHandler):
    @is_super_admin
    def post(self):
        email = self.request.get('email')
        asm_id = self.request.get('asm_id')
        ExtraAttempts.give_extra_attempt(email, asm_id)


class AsmAttemptsAPIHandler(BaseAPIHandler):
    """ Handlers for the route /api/student/attempts """
    _MODEL_HANDLER = AsmAttemptsModel
    _DTO_HANDLER = AsmAttemptsDTO
    _ID_KEYS = ['email']

    def get(self):
        email = self.request.get('email')
        email_clean = Students.clean_email(email)
        self.request.query_string = 'email=' + email_clean
        super(AsmAttemptsAPIHandler, self).get()
