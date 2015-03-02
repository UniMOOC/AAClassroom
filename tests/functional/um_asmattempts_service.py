
from datetime import datetime
from datetime import timedelta

from mock import patch
from mock import MagicMock

from functional import actions

from modules.um_assessments.model import AsmAttemptsDAO
from modules.um_assessments.model import AsmDateDAO
from modules.um_assessments.service import AsmAttempts
from modules.um_assessments.exceptions import NoDatesAvailable
from modules.um_assessments.exceptions import NoAttemptsLeft


EMAIL = 'test@example.com'
STUDENT = MagicMock(email=EMAIL)
MOCK_ATT = MagicMock(attempts_left={1: 1})
EDITION = MagicMock(key='madrid-02')

START = datetime.utcnow() - timedelta(days=1)
END = datetime.utcnow() + timedelta(days=1)
MOCK_DATE = MagicMock(
    id=1,
    edition='madrid-02',
    assessment="1",
    start_date=START,
    end_date=END
)
DATES_LIST = [
    MOCK_DATE
]


class AsmAttemptsTest(actions.TestBase):

    @patch.object(AsmAttemptsDAO, 'get', return_value=MagicMock())
    def test_get(self, mock_get):
        att = AsmAttempts.get(EMAIL)
        mock_get.assert_called_with(EMAIL)
        self.assertEquals(att, mock_get.return_value)

    @patch.object(AsmAttemptsDAO, 'set', return_value=MagicMock())
    def test_set(self, mock_set):
        AsmAttempts.set(MOCK_ATT)
        mock_set.assert_called_with(MOCK_ATT)

    @patch.object(AsmAttemptsDAO, 'create', return_value=MagicMock())
    @patch.object(AsmDateDAO, 'get_by_edition', return_value=DATES_LIST)
    def test_set_for_student(self, mock_get_by_edition, mock_create):
        AsmAttempts.set_for_student(STUDENT, EDITION)
        mock_get_by_edition.assert_called_with(EDITION.key)
        mock_create.assert_called_with(
            EMAIL, {MOCK_DATE.id: MOCK_DATE.attempts}
        )

    @patch.object(AsmDateDAO, 'get_by_id', return_value=MOCK_DATE)
    @patch.object(AsmAttemptsDAO, 'get')
    def test_check_attempts(self, mock_get, mock_get_by_id):
        mock_get.return_value = MagicMock(attempts_left={1: 1})
        AsmAttempts.check_attempts(STUDENT, EDITION.key, "1")
        mock_get.assert_called_with(STUDENT.email)
        mock_get_by_id.assert_called_with(1)

    @patch.object(AsmAttemptsDAO, 'set')
    @patch.object(AsmDateDAO, 'get_by_id', return_value=MOCK_DATE)
    @patch.object(AsmAttemptsDAO, 'get')
    def test_check_attempts_decreasing(
            self, mock_get, mock_get_by_id, mock_set):
        mock_get.return_value = MagicMock(attempts_left={1: 1})
        AsmAttempts.check_attempts(STUDENT, EDITION.key, "1", decrease=True)
        mock_get.assert_called_with(STUDENT.email)
        mock_get_by_id.assert_called_with(1)
        mock_set.assert_called_with(mock_get.return_value)

    @patch.object(AsmAttemptsDAO, 'get')
    def test_check_attempts_student_has_no_dates(
            self, mock_get):
        mock_get.return_value = MagicMock(attempts_left={1: 1})
        self.assertRaises(NoDatesAvailable, AsmAttempts.check_attempts,
                          STUDENT, EDITION.key, "1", decrease=True)
        mock_get.assert_called_with(STUDENT.email)

    @patch.object(AsmAttempts, '_is_for_edition_and_open', return_value=False)
    @patch.object(AsmAttemptsDAO, 'get')
    def test_check_attempts_no_dates(self, mock_get, mock_is_for):
        mock_get.return_value = MagicMock(attempts_left={1: 1})
        self.assertRaises(NoDatesAvailable, AsmAttempts.check_attempts,
                          STUDENT, EDITION.key, "1", decrease=True)

    @patch.object(AsmDateDAO, 'get_by_id', return_value=MOCK_DATE)
    @patch.object(AsmAttemptsDAO, 'get')
    def test_check_attempts_no_attempts(self, mock_get, mock_get_by_id):
        mock_get.return_value = MagicMock(attempts_left={1: 0})
        self.assertRaises(NoAttemptsLeft, AsmAttempts.check_attempts,
                          STUDENT, EDITION.key, "1", decrease=True)
