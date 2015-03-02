
import base64
from mock import patch
from mock import MagicMock

from functional import actions

from modules.um_assessments.service import ExtraAttempts
from modules.um_students.service import Students

from modules.um_assessments.exceptions import InvalidStudent
from modules.um_assessments.exceptions import InvalidAssessment
from modules.um_assessments.exceptions import InvalidHash


class ExtraAttemptsTest(actions.TestBase):
    def setUp(self):
        self.with_s = MagicMock(
            email='test@example.com',
            get_field=MagicMock(
                return_value={"1": base64.b64encode('test@example.com;1')}
            ),
            set_field=MagicMock()
        )

        self.wout_s = MagicMock(
            email='test@example.com',
            get_field=MagicMock(return_value={}),
            set_field=MagicMock()
        )

    def tearDown(self):
        pass

    @patch.object(Students, 'get_by_email')
    def test_generate_url(self, mock_get):
        mock_get.return_value = self.wout_s
        asm_id = "1"
        url = ExtraAttempts.give_extra_attempt(self.wout_s.email, asm_id)

        self.wout_s.set_field.assert_called_with(
            'extra_attempts',
            {"1": base64.b64encode('test@example.com;1')}
        )

        self.assertIsNotNone(url)

        url_hash = url.split('/')[-1]
        self.assertEquals(
            url_hash,
            base64.b64encode(self.wout_s.email + ';' + str(asm_id))
        )

    @patch.object(Students, 'get_by_email')
    def test_regenerate_url(self, mock_get):
        mock_get.return_value = self.with_s
        asm_id = "1"
        url = ExtraAttempts.give_extra_attempt(self.with_s.email, asm_id)

        self.assertFalse(self.with_s.set_field.called)

        self.assertIsNotNone(url)

        url_hash = url.split('/')[-1]
        self.assertEquals(
            url_hash,
            base64.b64encode(self.with_s.email + ';' + str(asm_id))
        )

    @patch.object(Students, 'get_by_email')
    def test_valid_hash_check(self, mock_get):
        mock_get.return_value = self.with_s
        email = self.with_s.email
        asm_id = "1"
        url_hash = base64.b64encode(email + ';' + str(asm_id))

        hash_asm_id = ExtraAttempts.unhash(email, url_hash)
        self.assertEquals(asm_id, hash_asm_id)

    @patch.object(Students, 'get_by_email')
    def test_invalid_student_hash_check(self, mock_get):
        mock_get.return_value = self.with_s
        email_1 = "test@example.com"
        email_2 = "test2@example.com"
        asm_id = "1"
        url_hash = base64.b64encode(email_2 + ';' + str(asm_id))

        self.assertRaises(
            InvalidStudent,
            ExtraAttempts.unhash,
            email_1, url_hash
        )

    @patch.object(Students, 'get_by_email')
    def test_invalid_assessment_hash_check(self, mock_get):
        mock_get.return_value = self.with_s
        email = self.with_s.email
        asm_id_2 = "2"
        url_hash = base64.b64encode(email + ';' + str(asm_id_2))

        self.assertRaises(
            InvalidAssessment,
            ExtraAttempts.unhash,
            email, url_hash
        )

    @patch.object(Students, 'get_by_email')
    def test_invalid_hash(self, mock_get):
        mock_get.return_value = self.with_s
        email = self.with_s.email
        url_hash = "test"

        self.assertRaises(
            InvalidHash,
            ExtraAttempts.unhash,
            email, url_hash
        )

    @patch.object(Students, 'get_by_email')
    def test_remove_attempt(self, mock_get):
        mock_get.return_value = self.with_s
        asm_id = "1"
        ExtraAttempts.remove_extra_attempt(self.with_s.email, asm_id)

        self.with_s.set_field.assert_called_with('extra_attempts', {})
