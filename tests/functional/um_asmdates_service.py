
from datetime import datetime
from datetime import timedelta

from mock import patch
from mock import MagicMock

from functional import actions

from modules.um_assessments.model import AsmDateDAO
from modules.um_assessments.service import AsmDates


START = datetime.utcnow() - timedelta(days=1)
END = datetime.utcnow() + timedelta(days=1)
BEFORE = datetime.utcnow() - timedelta(days=2)
AFTER = datetime.utcnow() + timedelta(days=2)

MOCK_DATE = MagicMock(start_date=START, end_date=END)
DATES_LIST = [
    MOCK_DATE
]


class AsmDatesTest(actions.TestBase):

    @patch.object(AsmDateDAO, 'create', return_value=MagicMock())
    def test_create(self, mock_create):
        asm_date = AsmDates.create('madrid-02', "1", START, END, 1)
        mock_create.assert_called_with('madrid-02', "1", START, END, 1, False)
        self.assertEquals(asm_date, mock_create.return_value)

    @patch.object(AsmDateDAO, 'get', return_value=MagicMock())
    def test_get(self, mock_get):
        asm_date = AsmDates.get('madrid-02', "1")
        mock_get.assert_called_with('madrid-02', "1")
        self.assertEquals(asm_date, mock_get.return_value)

    @patch.object(AsmDateDAO, 'get', return_value=DATES_LIST)
    def test_get_todays(self, mock_get):
        asm_date = AsmDates.get_todays('madrid-02', "1")
        mock_get.assert_called_with('madrid-02', "1")
        self.assertEquals(asm_date, MOCK_DATE)

    @patch.object(AsmDateDAO, 'get', return_value=DATES_LIST)
    @patch.object(AsmDates, '_utcnow', return_value=BEFORE)
    def test_get_todays_before_date(self, mock_now, mock_get):
        asm_date = AsmDates.get_todays('madrid-02', "1")
        mock_get.assert_called_with('madrid-02', "1")
        self.assertIsNone(asm_date)

    @patch.object(AsmDateDAO, 'get', return_value=DATES_LIST)
    @patch.object(AsmDates, '_utcnow', return_value=AFTER)
    def test_get_todays_after_date(self, mock_now, mock_get):
        asm_date = AsmDates.get_todays('madrid-02', "1")
        mock_get.assert_called_with('madrid-02', "1")
        self.assertIsNone(asm_date)

    @patch.object(AsmDates, 'get_todays', return_value=MOCK_DATE)
    def test_is_open(self, mock_todays):
        is_open = AsmDates.is_open('madrid-02', "1")
        mock_todays.assert_called_with('madrid-02', "1")
        self.assertTrue(is_open)

    @patch.object(AsmDates, 'get_todays', return_value=None)
    def test_is_not_open(self, mock_todays):
        is_open = AsmDates.is_open('madrid-02', "1")
        mock_todays.assert_called_with('madrid-02', "1")
        self.assertFalse(is_open)

