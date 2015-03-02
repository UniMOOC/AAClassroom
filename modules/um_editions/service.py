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

from datetime import timedelta
from datetime import datetime

from modules.um_assessments.service import AsmAttempts
from modules.um_assessments.service import AsmDates
from modules.um_common.utils import get_month_name
from modules.um_common.utils import TimeHelper
from modules.um_certificates.service import AssessmentCertificates
from .model import EditionDAO as DAO
from .exceptions import *


class Editions(object):
    @classmethod
    def get(cls, edition_key):
        return DAO.get(edition_key)

    @classmethod
    def create_edition(cls, edition_code, start_date):
        ed_type = cls._get_type(edition_code)

        if not EditionsDatesFactory.is_edition_type_supported(ed_type):
            raise UnsupportedEditionType(
                "Edition type '{}' is not supported".format(ed_type)
            )

        name = cls._get_name(edition_code)
        edition = DAO.create(edition_code, name)

        EditionsDatesFactory.create_edition_data(
            edition_code, start_date)

        return edition

    @classmethod
    def register_user(cls, edition_code, student):
        edition = DAO.get(edition_code)
        if not edition:
            return None

        cls._add_student_field(edition, student)
        cls._add_to_edition(edition, student)
        AsmAttempts.set_for_student(student, edition)

    @classmethod
    def get_edition_of_student(cls, student):
        return student.get_field('editions', [])[-1]

    @classmethod
    def _add_student_field(cls, edition, student):
        editions = student.get_field('editions', [])

        if edition.key not in editions:
            editions.append(edition.key)

        student.set_field('editions', editions)

    @classmethod
    def _add_to_edition(cls, edition, student):
        email = student.email.lower()
        if email not in edition.users:
            edition.users.append(email)

        DAO.set(edition)

    @classmethod
    def _get_name(cls, edition_code):
        _, _, city, month = edition_code.split('-')
        name = "{} - {}".format(
            city.capitalize(),
            get_month_name(month, 'es_ES')
        )
        return name

    @classmethod
    def _get_type(cls, edition_code):
        _, edition_type, _, _ = edition_code.split('-')
        return edition_type


class EditionsDatesFactory(object):
    ESP_COURSE_DATES_SCHEMES = [
        {
            "assessments": [
                {
                    "id": "2",
                    "attemps": 1,
                    "start_displacement": timedelta(),
                    "end_displacement": timedelta(1)
                },
                {
                    "id": "3",
                    "attemps": 1,
                    "start_displacement": timedelta(1),
                    "end_displacement": timedelta(2)
                }
            ],
            "badge_id": "mkd-esp-asist-disp"
        },
        {
            "assessments": [
                {
                    "id": "5",
                    "attemps": 1,
                    "start_displacement": timedelta(2),
                    "end_displacement": timedelta(3)
                },
                {
                    "id": "6",
                    "attemps": 1,
                    "start_displacement": timedelta(3),
                    "end_displacement": timedelta(4)
                },
                {
                    "id": "7",
                    "attemps": 1,
                    "start_displacement": timedelta(4),
                    "end_displacement": timedelta(5)
                }
            ],
            "badge_id": "mkd-esp-asist-seo"
        },
        {
            "assessments": [
                {
                    "id": "9",
                    "attemps": 1,
                    "start_displacement": timedelta(7),
                    "end_displacement": timedelta(8)
                },
                {
                    "id": "10",
                    "attemps": 1,
                    "start_displacement": timedelta(8),
                    "end_displacement": timedelta(9)
                },
                {
                    "id": "11",
                    "attemps": 1,
                    "start_displacement": timedelta(9),
                    "end_displacement": timedelta(10)
                }
            ],
            "badge_id": "mkd-esp-asist-commerce"
        },
        {
            "assessments": [
                {
                    "id": "13",
                    "attemps": 1,
                    "start_displacement": timedelta(10),
                    "end_displacement": timedelta(11)
                },
                {
                    "id": "14",
                    "attemps": 1,
                    "start_displacement": timedelta(11),
                    "end_displacement": timedelta(12)
                }
            ],
            "badge_id": "mkd-esp-asist-redes"
        },
        {
            "assessments": [
                {
                    "id": "17",
                    "attemps": 1,
                    "start_displacement": timedelta(14),
                    "end_displacement": timedelta(15)
                },
                {
                    "id": "18",
                    "attemps": 1,
                    "start_displacement": timedelta(15),
                    "end_displacement": timedelta(16)
                }
            ],
            "badge_id": "mkd-esp-asist-mobile"
        },
        {
            "assessments": [
                {
                    "id": "21",
                    "attemps": 1,
                    "start_displacement": timedelta(16),
                    "end_displacement": timedelta(17)
                },
                {
                    "id": "22",
                    "attemps": 1,
                    "start_displacement": timedelta(17),
                    "end_displacement": timedelta(18)
                },
                {
                    "id": "23",
                    "attemps": 1,
                    "start_displacement": timedelta(18),
                    "end_displacement": timedelta(19)
                }
            ],
            "badge_id": "mkd-esp-asist-analit"
        },
        {
            "assessments": [
                {
                    "id": "24",
                    "attemps": 2,
                    "start_displacement": timedelta(19),
                    "end_displacement": timedelta(24)
                }
            ],
            "badge_id": "mkd-esp-final"
        }
    ]

    BAS_COURSE_DATES_SCHEMES = [
        {
            "ids": ["2", "3"],
            "start": timedelta(0)
        },
        {
            "ids": ["9", "22", "11"],
            "start": timedelta(1)
        },
        {
            "ids": ["5", "6"],
            "start": timedelta(2)
        },
        {
            "ids": ["13", "14", "16"],
            "start": timedelta(3)
        },
        {
            "ids": ["18", "19", "20"],
            "start": timedelta(4)
        }
    ]

    @classmethod
    def is_edition_type_supported(cls, edition_type):
        return edition_type in ['esp', 'bas']

    @classmethod
    def create_edition_data(cls, edition, date_start):
        ed_type = Editions._get_type(edition)
        if ed_type == 'esp':
            return cls.create_esp_edition(edition, date_start)
        elif ed_type == 'bas':
            return cls.create_bas_edition(edition, date_start)

    @classmethod
    def create_bas_edition(cls, edition, date_start):
        end = cls._displace_date(date_start, timedelta(7), hour=18)
        for day in cls.BAS_COURSE_DATES_SCHEMES:
            for asm_id in day["ids"]:
                start = cls._displace_date(date_start, day["start"], hour=18)
                AsmDates.create(edition, asm_id, start, end, 3, True)

    @classmethod
    def create_esp_edition(cls, edition, date_start):
        for unit in cls.ESP_COURSE_DATES_SCHEMES:
            for asm in unit['assessments']:
                asm_start = cls._displace_date(
                    date_start, asm["start_displacement"], hour=18
                )
                asm_end = cls._displace_date(
                    date_start, asm["end_displacement"], hour=8
                )

                AsmDates.create(
                    edition, asm["id"], asm_start,
                    asm_end, asm["attemps"], (asm['id'] != '24'))

                last_start = cls._last_week_start(date_start)
                last_end = cls._last_week_end(date_start)
                if asm['id'] != '24':
                    AsmDates.create(
                        edition, asm["id"], last_start,
                        last_end, 1, False)

            u_start = date_start + unit["assessments"][0]["start_displacement"]
            u_end = date_start + unit["assessments"][-1]["end_displacement"]
            AssessmentCertificates.create(
                edition,
                cls._assessments_to_list(unit["assessments"]),
                unit["badge_id"],
                u_start,
                u_end,
                False)

    @classmethod
    def create_one_day_edition_data(cls, edition, date_start):
        for unit in cls.ESP_COURSE_DATES_SCHEMES:
            for asm in unit['assessments']:
                asm_start = cls._displace_date(
                    date_start, timedelta(days=0), hour=0
                )
                asm_end = cls._displace_date(
                    date_start, timedelta(days=1), hour=0
                )

                AsmDates.create(
                    edition, asm["id"], asm_start,
                    asm_end, asm["attemps"], True)

                last_start = date_start + timedelta(days=1)
                last_end = date_start + timedelta(days=2)
                if asm['id'] != '24':
                    AsmDates.create(
                        edition, asm["id"], last_start,
                        last_end, 1, True)

            u_start = date_start + timedelta(days=0)
            u_end = date_start + timedelta(days=1)
            AssessmentCertificates.create(
                edition,
                cls._assessments_to_list(unit["assessments"]),
                unit["badge_id"],
                u_start,
                u_end,
                False)

    @classmethod
    def _assessments_to_list(cls, assessments):
        return [asm["id"] for asm in assessments]

    @classmethod
    def _last_week_start(cls, date_start):
        final_asm = cls.ESP_COURSE_DATES_SCHEMES[-1]["assessments"][-1]
        return cls._displace_date(
            date_start, final_asm["start_displacement"], hour=9
        )

    @classmethod
    def _last_week_end(cls, date_start):
        final_asm = cls.ESP_COURSE_DATES_SCHEMES[-1]["assessments"][-1]
        return cls._displace_date(
            date_start, final_asm["end_displacement"], hour=8
        )

    @classmethod
    def _displace_date(cls, date, displacement, hour=None):
        date = date + displacement
        if hour is not None:
            date = datetime(
                year=date.year, month=date.month, day=date.day, hour=hour
            )
            date = TimeHelper.from_GMT1(date)

        return date
