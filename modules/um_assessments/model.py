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
from datetime import datetime

from google.appengine.ext import db

from models.models import MemcacheManager

from modules.um_common.utils import TimeHelper


DATES_MEM_KEY = 'asm_dates-{}'


class AsmDateModel(db.Model):
    """ Dates of availability for the assessments
        For each assessment in an edition there will be a range (or number of
        ranges) in which students of that edition can attempt the assessment.
    """

    edition = db.StringProperty()
    assessment = db.StringProperty()
    start_date = db.DateTimeProperty()
    end_date = db.DateTimeProperty()
    attempts = db.IntegerProperty()
    check_attendance = db.BooleanProperty()


class AsmDateDTO(object):
    def __init__(self, asm_date):
        self.id = asm_date.key().id()
        self.edition = asm_date.edition
        self.assessment = asm_date.assessment
        self.start_date = asm_date.start_date
        self.end_date = asm_date.end_date
        self.attempts = asm_date.attempts
        self.check_attendance = asm_date.check_attendance

    def pseudo_key(self, dates_in_gmt1=False):
        start_date = self.start_date
        end_date = self.end_date

        if dates_in_gmt1:
            start_date = TimeHelper.to_GMT1(start_date)
            end_date = TimeHelper.to_GMT1(end_date)

        return "{};{};{};{}".format(
            self.edition, self.assessment,
            start_date.isoformat(), end_date.isoformat()
        )

    def is_open(self, date=None):
        if not date:
            date = datetime.utcnow()
        return self.start_date <= date <= self.end_date


class AsmDateDAO(object):

    @classmethod
    def get(cls, edition, assessment):
        dates = cls._from_memcache(edition)
        return [date for date in dates if date.assessment == assessment]

    @classmethod
    def get_by_edition(cls, edition):
        return cls._from_memcache(edition)

    @classmethod
    def get_by_id(cls, asm_date_id):
        asm_date = AsmDateModel.get_by_id(int(asm_date_id))
        if asm_date:
            return AsmDateDTO(asm_date)

    @classmethod
    def create(cls, edition, asm_id, start_date, end_date,
               attempts, check_attendance=False):
        model = AsmDateModel(
            edition=edition, assessment=asm_id, start_date=start_date,
            end_date=end_date, attempts=attempts,
            check_attendance=check_attendance
        )
        model.put()
        return AsmDateDTO(model)

    @classmethod
    def _from_memcache(cls, edition):
        mem_key = DATES_MEM_KEY.format(edition)
        dates = MemcacheManager.get(mem_key)
        if not dates:
            dates = [AsmDateDTO(asm_date) for asm_date
                     in AsmDateModel.all().filter('edition =', edition)]
            MemcacheManager.set(mem_key, dates)
        return dates


class AsmAttemptsModel(db.Model):
    """ Model which determines how many times a student can attempt to
        try an assessment in a given date range (given by AsmDateModel)
    """
    email = db.StringProperty(indexed=True, default='')
    attempts_left = db.TextProperty()


class AsmAttemptsDTO():
    def __init__(self, asm_attempts):
        self.email = asm_attempts.email
        self.attempts_left = json.loads(asm_attempts.attempts_left)


class AsmAttemptsDAO():

    @classmethod
    def get(cls, email):
        model = cls._get_model(email)
        if model:
            return AsmAttemptsDTO(model)

    @classmethod
    def _get_model(cls, email):
        return AsmAttemptsModel.all().filter(
            'email =', email
        ).get()

    @classmethod
    def create(cls, email, attempts_left):
        return AsmAttemptsDTO(
            cls._create_model(email, json.dumps(attempts_left))
        )

    @classmethod
    def _create_model(cls, email, attempts_left):
        model = AsmAttemptsModel(email=email, attempts_left=attempts_left)
        model.put()
        return model

    @classmethod
    def set(cls, dto):
        model = cls._get_model(dto.email)
        if not model:
            model = cls._create_model(dto.email)

        model.attempts_left = json.dumps(dto.attempts_left)
        model.put()
