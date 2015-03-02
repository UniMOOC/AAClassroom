
from datetime import datetime
from datetime import timedelta
from mock import patch
from mock import MagicMock

from functional import actions

from modules.um_assessments.model import AsmDateDAO
from modules.um_assessments.model import AsmDateModel


START = datetime.utcnow()
END = datetime.utcnow() + timedelta(days=1)

MOCK_DB_MODEL = MagicMock()
MOCK_DB_MODEL.put = MagicMock()
MOCK_DB_MODEL.key.id.return_value = 0


class AsmDatesDAOTest(actions.TestBase):

    def test_create(self):
        asm_date = AsmDateDAO.create('madrid-02', "1", START, END, 1)
        self.assertIsNotNone(asm_date)
        self.assertEqual(asm_date.start_date, START)
        self.assertEqual(asm_date.end_date, END)
        self.assertEqual(asm_date.attempts, 1)

    def test_create_and_get(self):
        AsmDateDAO.create('madrid-02', "1", START, END, 1)
        asm_dates = AsmDateDAO.get('madrid-02', "1")
        self.assertEquals(len(asm_dates), 1)
        self.assertEquals(asm_dates[0].start_date, START)
        self.assertEquals(asm_dates[0].end_date, END)
        self.assertEquals(asm_dates[0].attempts, 1)

    def test_get_empty(self):
        asm_dates = AsmDateDAO.get('madrid-02', "1")
        self.assertEquals(len(asm_dates), 0)

    def test_get_by_edition(self):
        AsmDateDAO.create('madrid-02', "1", START, END, 1)
        asm_dates = AsmDateDAO.get_by_edition('madrid-02')
        self.assertEquals(len(asm_dates), 1)
        self.assertEquals(asm_dates[0].start_date, START)
        self.assertEquals(asm_dates[0].end_date, END)
        self.assertEquals(asm_dates[0].attempts, 1)

    def test_get_by_edition_empty(self):
        AsmDateDAO.create('madrid-02', "1", START, END, 1)
        asm_dates = AsmDateDAO.get_by_edition('madrid-03')
        self.assertEquals(len(asm_dates), 0)

    def test_get_by_id(self):
        asm_date = AsmDateDAO.create('madrid-02', "1", START, END, 1)
        asm_date = AsmDateDAO.get_by_id(asm_date.id)
        self.assertIsNotNone(asm_date)
        self.assertEqual(asm_date.start_date, START)
        self.assertEqual(asm_date.end_date, END)
        self.assertEqual(asm_date.attempts, 1)

    def test_get_by_id_fail(self):
        asm_date = AsmDateDAO.create('madrid-02', "1", START, END, 1)
        asm_date = AsmDateDAO.get_by_id(asm_date.id + 1)
        self.assertIsNone(asm_date)
