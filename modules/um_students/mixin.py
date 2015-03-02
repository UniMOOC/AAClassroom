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
import datetime

from modules.um_assessments.service import Assessments
from modules.um_gobalo.service import GobaloAPI
from modules.um_course.service import Courses
from .exceptions import TooManyMissedDays
from .exceptions import NoClassAttendance


class StudentMixin(object):
    def acreditations_email(self):
        return self.get_field('acreditations_email')

    def original_email(self):
        return self.get_field('original_email')

    def complete_name(self):
        return self.name

    def get_field(self, field, default_value=None):
        fields = json.loads(self.additional_fields)
        return fields.get(field, default_value)

    def set_field(self, key, value):
        fields = json.loads(self.additional_fields)
        fields[key] = value
        self.additional_fields = json.dumps(fields)
        self.put()

    def get_scores(self):
        return json.loads(self.scores) if self.scores else {}

    def is_assessment_pass(self, asm_id):
        score = self.get_scores().get(asm_id, 0)
        asm = Assessments.find_unit_by_id(asm_id)
        return score >= float(asm.min_score)

    def has_attempted_assessment(self, asm_id):
        scores = self.get_scores()
        return scores.get(asm_id, None) is not None

    def get_course_progress(self):
        from modules.um_assessments.service import AsmAttempts
        from modules.um_assessments.service import AsmDates
        from modules.um_editions.service import Editions

        progress = {str(asm.unit_id): {'attempts': {}, 'score': None}
                    for asm in Courses.get_assessments()}

        scores = self.get_scores()
        for asm_id, score in scores.iteritems():
            progress[asm_id]['score'] = score

        student_edition = Editions.get_edition_of_student(self)
        student_attempts = AsmAttempts.get(self.email)

        edition_dates = AsmDates.get_by_edition(student_edition)
        for asm_date in edition_dates:
            progress_dates = progress.get(asm_date.assessment, {})
            att_left = student_attempts.attempts_left[str(asm_date.id)]
            key = asm_date.pseudo_key(dates_in_gmt1=True)
            progress_dates['attempts'][key] = att_left
            progress[asm_date.assessment] = progress_dates

        return progress

    def check_today_attended(self):
        attended_days = self.get_field(
            'attended_days',
            {'days': [], 'too_many_missed_days': False}
        )
        if attended_days['too_many_missed_days']:
            raise TooManyMissedDays()

        date = datetime.datetime.utcnow()
        # TODO: (martin) make the hour check generic somehow
        if date.hour <= 7:  # 08:00 in GMT+1
            date -= datetime.timedelta(days=1)

        if date.weekday() == 5:  # if it's a Saturday
            date -= datetime.timedelta(days=1)  # Make it a Friday
        elif date.weekday() == 6:  # if it's a Sunday
            date -= datetime.timedelta(days=2)  # Make it a Friday

        date_str = date.strftime('%Y-%m-%d')
        if date_str not in attended_days['days']:
            status = GobaloAPI.user_attended(self.original_email(), date)
            if status == 'ATTENDED':
                attended_days['days'].append(date_str)
                self.set_field('attended_days', attended_days)
            elif status == 'TOO_MANY_MISSES':
                attended_days['too_many_misses'] = True
                self.set_field('attended_days', attended_days)
                raise TooManyMissedDays()
            elif status == 'DIDNT_ATTEND':
                raise NoClassAttendance()
