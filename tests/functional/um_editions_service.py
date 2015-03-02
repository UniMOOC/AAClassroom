
from datetime import datetime, timedelta

from functional import actions
from models import models

import modules.um_editions.service as ed_service
from modules.um_editions import exceptions
from modules.um_assessments.service import AsmDates


ASM_SCHEMA = {
    'esp': [
        ['1', timedelta(), timedelta(days=1), 1, True],
        ['1', timedelta(), timedelta(days=2), 3, True],
        ['2', timedelta(), timedelta(days=1), 1, True],
        ['2', timedelta(), timedelta(days=2), 3, True]
    ],
    'bas': [
        ['1', timedelta(), timedelta(days=1), 10]
    ]
}

ed_service.asm_schemas = ASM_SCHEMA
start_date = datetime.utcnow()


class EditionsServiceTest(actions.TestBase):

    def test_esp_create_and_get(self):
        edition = ed_service.Editions.create_edition(
            'md-esp-barcelona-03', start_date
        )

        dates = AsmDates.get_by_edition(edition.key)
        self.assertEqual(len(dates), 4)

        for date in dates:
            self.assertEqual(date.start_date, start_date)
            if date.attempts == 1:
                self.assertEqual(date.end_date, start_date + timedelta(1))
            elif date.attempts == 3:
                self.assertEqual(date.end_date, start_date + timedelta(2))

    def test_bas_create_and_get(self):
        edition = ed_service.Editions.create_edition(
            'md-bas-barcelona-03', start_date
        )

        dates = AsmDates.get_by_edition(edition.key)
        self.assertEqual(len(dates), 1)

        self.assertEqual(dates[0].start_date, start_date)
        self.assertEqual(dates[0].end_date, start_date + timedelta(1))

    def test_create_bad_type(self):
        self.assertRaises(
            exceptions.UnsupportedEditionType,
            ed_service.Editions.create_edition,
            'md-pot-barcelona-03', start_date
        )

        self.assertIsNone(ed_service.Editions.get('barcelona-03'))

    def test_create_duplicate_edition_fails(self):
        ed_service.Editions.create_edition(
            'md-bas-barcelona-03', start_date
        )
        self.assertRaises(
            exceptions.EditionAlreadyExists,
            ed_service.Editions.create_edition,
            'md-bas-barcelona-03', start_date
        )

    # def test_register_user(self):
    #     pass
    #     edition = ed_service.Editions.create_edition(
    #         'md-bas-barcelona-03', start_date
    #     )

    #     s = models.Student.add_new_student_for_current_user(
    #         'Test User', None, self
    #     )

    #     ed_service.Editions.register_user()
