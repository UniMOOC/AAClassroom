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

from __future__ import division

import json
import base64
import datetime

from models.models import StudentAnswersEntity
from models import utils

from modules.um_common.utils import ConfigReader
from modules.um_students.service import Students

from .model import AsmAttemptsDAO as AttDAO
from .model import AsmDateDAO as DateDAO
from .exceptions import NoAttemptsLeft
from .exceptions import NoDatesAvailable
from .exceptions import InvalidStudent
from .exceptions import InvalidAssessment
from .exceptions import InvalidHash
from modules.um_course.service import Courses


DEFAULT_MAX_ATTEMPTS = 3


class AsmDates(object):
    @classmethod
    def get(cls, edition, assessment):
        return DateDAO.get(edition, assessment)

    @classmethod
    def get_by_edition(cls, edition):
        return DateDAO.get_by_edition(edition)

    @classmethod
    def get_todays(cls, edition, assessment):
        dates = DateDAO.get(edition, assessment)
        now = cls._utcnow()
        for date in dates:
            if date.start_date <= now <= date.end_date:
                return date

    @classmethod
    def is_open(cls, edition, assessment, date=None):
        if not date:
            date = cls._utcnow()

        return cls.get_todays(edition, assessment) is not None

    @classmethod
    def create(cls, edition, unit_id, start, end, attempts,
               check_attendance=False):
        return DateDAO.create(
            edition, unit_id, start, end, attempts, check_attendance
        )

    @classmethod
    def _utcnow(cls):
        return datetime.datetime.utcnow()


class AsmAttempts(object):
    config = ConfigReader('modules/um_assessment/config.yaml')

    @classmethod
    def check_attempts(
            cls, student, edition_key, asm_id, decrease=False):
        attempts = AttDAO.get(student.email)
        if attempts is None:
            raise NoDatesAvailable()

        for asm_date_id, att_left in attempts.attempts_left.iteritems():
            asm_date = DateDAO.get_by_id(asm_date_id)
            if cls._is_for_edition_and_open(asm_date, edition_key, asm_id):
                if att_left == 0:
                    raise NoAttemptsLeft()
                else:
                    if decrease:
                        attempts.attempts_left[asm_date_id] = att_left - 1
                        AttDAO.set(attempts)
                    return
        raise NoDatesAvailable()

    @classmethod
    def _is_for_edition_and_open(cls, asm_date, edition, asm_id):
        return (asm_date and asm_date.edition == edition
                and asm_date.assessment == asm_id and asm_date.is_open())

    @classmethod
    def get(cls, email):
        return AttDAO.get(email)

    @classmethod
    def set(cls, dto):
        return AttDAO.set(dto)

    @classmethod
    def set_for_student(cls, student, edition):
        asm_dates = DateDAO.get_by_edition(edition.key)

        attempts = {ad.id: ad.attempts for ad in asm_dates}

        AttDAO.create(student.email, attempts)


class ExtraAttempts(object):
    config = ConfigReader('modules/um_assessments/config.yaml')

    @classmethod
    def give_extra_attempt(cls, student_email, asm_id):
        student = Students.get_by_email(student_email)
        if not student:
            return None

        extra_attempts = student.get_field('extra_attempts', {})
        url_hash = extra_attempts.get(asm_id, None)
        if url_hash is None:
            url_hash = cls._hash(student.email, asm_id)
            extra_attempts[asm_id] = url_hash
            student.set_field('extra_attempts', extra_attempts)

        return cls.config['extra_attempts_url'].format(url_hash)

    @classmethod
    def unhash(cls, student_email, url_hash):
        student = Students.get_by_email(student_email)
        if not student:
            return None

        hash_email, asm_id = cls._unhash(url_hash)

        if student.email != hash_email:
            raise InvalidStudent

        if asm_id not in student.get_field('extra_attempts', {}):
            raise InvalidAssessment

        return asm_id

    @classmethod
    def remove_extra_attempt(cls, student_email, asm_id):
        student = Students.get_by_email(student_email)
        if not student:
            return None

        extra_attempts = student.get_field('extra_attempts', {})
        if asm_id in extra_attempts:
            del extra_attempts[asm_id]
            student.set_field('extra_attempts', extra_attempts)

    @classmethod
    def _hash(cls, email, asm_id):
        return base64.b64encode("{};{}".format(email, asm_id))

    @classmethod
    def _unhash(cls, url_hash):
        try:
            values = base64.b64decode(url_hash).split(";")
            if len(values) != 2:
                raise InvalidHash
            return values
        except TypeError:
            raise InvalidHash


class Assessments(object):
    @classmethod
    def find_unit_by_id(cls, unit_id):
        unit = Courses.find_unit_by_id(unit_id)
        if unit and isinstance(unit.html_content, basestring):
            unit.html_content = json.loads(unit.html_content)
        return unit

    @classmethod
    def grade(cls, questions, answers):
        total = len(questions)
        correct = 0
        not_answered = 0
        feedback = []

        for question in questions:
            answer = answers.get(str(question['key']))
            q = {'question': question['question']}
            if answer is not None:
                if answer == question['correct']:
                    correct += 1
                    q['type'] = 'correct'
                else:
                    q['type'] = 'wrong'
                    q['choice'] = question['options'][int(answer)]
            else:
                not_answered += 1
                q['type'] = 'not_answered'
            feedback.append(q)

        # wrong = total - correct - not_answered
        score = round((correct / total) * 100, 2)

        # We're calculating values not yet used
        return score, feedback

    @classmethod
    def grade_and_update_score(cls, questions, new_answers, student, asm_id):
        """ Grade the assessment, update the student scores and
            issue the badge

            It calculate the grade get it in the assessments
        """
        cls.update_student_answers_entity(student, asm_id, new_answers)
        new_score, feedback = cls.grade(questions, new_answers)
        cls.update_student_scores(student, asm_id, new_score)
        return new_score, feedback

    @classmethod
    def update_student_answers_entity(cls, student, asm_id, new_answers):
        answers = StudentAnswersEntity.get_by_key_name(student.user_id)
        if not answers:
            answers = StudentAnswersEntity(key_name=student.user_id)
        answers.updated_on = datetime.datetime.now()

        utils.set_answer(answers, asm_id, new_answers)
        answers.put()

    @classmethod
    def update_student_scores(cls, student, asm_id, new_score):
        scores = json.loads(student.scores) if student.scores else {}
        scores[asm_id] = max(new_score, scores.get(asm_id, 0))
        student.scores = json.dumps(scores)
        student.put()
