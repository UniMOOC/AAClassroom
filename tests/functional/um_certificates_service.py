import datetime

from functional import actions

from modules.um_students.service import Students
from modules.um_assessments.service import Assessments

from modules.um_badges.model import SentBadge
from modules.um_badges.service import Badges
from modules.um_certificates.model import\
    AssessmentCertificate, AssessmentCertificateDTO
from modules.um_certificates.service import AssessmentCertificates

from mock import patch
from mock import MagicMock


class AssessmentCertificatesTest(actions.TestBase):

    _CERT_A = AssessmentCertificate(
        badge_id='A',
        assessments=['asm1', 'asm10'],
        date_start=datetime.datetime.strptime(
            '2015-01-13 10:39:43.070580', "%Y-%m-%d %H:%M:%S.%f"),
        date_end=datetime.datetime.strptime(
            '2015-01-23 10:39:43.070580', "%Y-%m-%d %H:%M:%S.%f"),
        edition='alicante')

    _CERT_B = AssessmentCertificate(
        badge_id='A',
        assessments=['asm1', 'asm2', 'asm3'],
        date_start=datetime.datetime.strptime(
            '2011-12-13 10:39:43.070580', "%Y-%m-%d %H:%M:%S.%f"),
        date_end=datetime.datetime.strptime(
            '2014-12-13 10:39:43.070580', "%Y-%m-%d %H:%M:%S.%f"),
        edition='alicante')

    _CERT_C = AssessmentCertificate(
        badge_id='B',
        assessments=['asm-final'],
        date_start=datetime.datetime.strptime(
            '2013-12-13 10:39:43.070580', "%Y-%m-%d %H:%M:%S.%f"),
        date_end=datetime.datetime.strptime(
            '2014-12-13 10:39:43.070580', "%Y-%m-%d %H:%M:%S.%f"),
        edition='barcelona')

    _CERT_D = AssessmentCertificate(
        badge_id='C',
        assessments=['asm1'],
        date_start=None,
        date_end=None,
        edition='alicante')

    _CERT_D_1 = AssessmentCertificate(
        badge_id='D',
        assessments=['asm1'],
        date_start=None,
        date_end=None,
        edition='alicante')

    _CERT_E = AssessmentCertificate(
        badge_id='A',
        assessments=['asm3'],
        date_start=None,
        date_end=datetime.datetime.strptime(
            '2014-12-13 10:39:43.070580', "%Y-%m-%d %H:%M:%S.%f"),
        edition='alicante')

    _CERT_F = AssessmentCertificate(
        badge_id='A',
        assessments=['asm3'],
        date_start=datetime.datetime.strptime(
            '2016-12-13 10:39:43.070580', "%Y-%m-%d %H:%M:%S.%f"),
        date_end=None,
        edition='alicante')

    _CERT_G = AssessmentCertificate(
        badge_id='A',
        assessments=['asm3'],
        date_start=None,
        date_end=datetime.datetime.strptime(
            '2015-12-23 10:39:43.070580', "%Y-%m-%d %H:%M:%S.%f"),
        edition='alicante')

    _CERT_H = AssessmentCertificate(
        badge_id='A',
        assessments=['asm3'],
        date_start=datetime.datetime.strptime(
            '2014-12-13 10:39:43.070580', "%Y-%m-%d %H:%M:%S.%f"),
        date_end=None,
        edition='alicante')

    _CERT_I = AssessmentCertificate(
        badge_id='permanent',
        assessments=['asm-badge'],
        date_start=None,
        date_end=None,
        edition='')

    _CERT_J = AssessmentCertificate(
        badge_id='specific',
        assessments=['asm-badge'],
        date_start=datetime.datetime.strptime(
            '2014-12-13 10:39:43.070580', "%Y-%m-%d %H:%M:%S.%f"),
        date_end=datetime.datetime.strptime(
            '2016-12-13 10:39:43.070580', "%Y-%m-%d %H:%M:%S.%f"),
        edition='specific')

    _CERT_LIST = [_CERT_A, _CERT_B, _CERT_C, _CERT_D, _CERT_E, _CERT_F,
                  _CERT_G, _CERT_H, _CERT_D_1, _CERT_I, _CERT_J]

    _ASM_1 = MagicMock()

    def setUp(self):
        super(AssessmentCertificatesTest, self).setUp()
        for cert in self._CERT_LIST:
            cert.put()
        self._ASM_1.min_score = '80.0'

    @patch.object(
        AssessmentCertificateDTO,
        'get_now',
        return_value=datetime.datetime(2015, 1, 14))
    def test_get_actives_by_assessment(self, mock_time):
        certs = AssessmentCertificates.\
            get_actives_by_assessment_in_edition('asm1', 'alicante')
        self.assertEqual(len(certs), 3)
        certs = AssessmentCertificates.\
            get_actives_by_assessment_in_edition('asm3', 'alicante')
        self.assertEqual(len(certs), 2)
        certs = AssessmentCertificates.\
            get_actives_by_assessment_in_edition('asm2', 'alicante')
        self.assertEqual(len(certs), 0)

    @patch.object(Badges, 'deferred_send_badge')
    @patch.object(Students, 'is_assessment_pass', return_value=True)
    @patch.object(
        AssessmentCertificateDTO,
        'get_now',
        return_value=datetime.datetime(2015, 1, 14))
    def test_give_badge(self, mock_taskqueue, mock_student, mock_time):
        student = MagicMock()
        student.email = 'test@example.com'
        student.name = 'Rodrigo de los tests'

        AssessmentCertificates.\
            issue_certificates_by_assessment(
                student, 'asm1', 'alicante')

        badges_ids = Badges.get_badges_of_student(student.email)
        self.assertEqual(len(badges_ids), 3)
        self.assertTrue(self._CERT_A.badge_id in badges_ids)
        self.assertTrue(self._CERT_D.badge_id in badges_ids)
        self.assertTrue(self._CERT_D_1.badge_id in badges_ids)
        sents = SentBadge.all()
        sents = [sent for sent in sents]
        self.assertEqual(len(sents), 3)

    @patch.object(Badges, 'deferred_send_badge')
    @patch.object(Assessments, 'find_unit_by_id', return_value=_ASM_1)
    @patch.object(
        AssessmentCertificateDTO,
        'get_now',
        return_value=datetime.datetime(2015, 1, 14))
    def test_give_half_badge(self, mock_taskqueue, mock_assessment, mock_time):
        student = MagicMock()
        student.email = 'test@example.com'
        student.name = 'Rodrigo de los tests'
        student.scores = '{"asm1":100}'

        AssessmentCertificates.\
            issue_certificates_by_assessment(
                student, 'asm1', 'alicante')

        badges_ids = Badges.get_badges_of_student(student.email)
        self.assertEqual(len(badges_ids), 2)
        self.assertTrue(self._CERT_D.badge_id in badges_ids)
        self.assertTrue(self._CERT_D_1.badge_id in badges_ids)
        sents = SentBadge.all()
        sents = [sent for sent in sents]
        self.assertEqual(len(sents), 2)

    @patch.object(Badges, 'deferred_send_badge')
    @patch.object(Assessments, 'find_unit_by_id', return_value=_ASM_1)
    @patch.object(
        AssessmentCertificateDTO,
        'get_now',
        return_value=datetime.datetime(2015, 1, 14))
    def test_not_give_badge(self, mock_taskqueue, mock_assessment, mock_time):
        student = MagicMock()
        student.email = 'test@example.com'
        student.name = 'Rodrigo de los tests'
        student.scores = '{"asm1":20}'

        AssessmentCertificates.\
            issue_certificates_by_assessment(
                student, 'asm1', 'alicante')

        badges = Badges.get_badges_of_student(student.email)
        self.assertEqual(len(badges), 0)
        sents = SentBadge.all()
        sents = [sent for sent in sents]
        self.assertEqual(len(sents), 0)

    @patch.object(Badges, 'deferred_send_badge')
    @patch.object(Assessments, 'find_unit_by_id', return_value=_ASM_1)
    @patch.object(
        AssessmentCertificateDTO,
        'get_now',
        return_value=datetime.datetime(2015, 1, 14))
    def test_give_badge_permanent(
            self, mock_taskqueue, mock_assessment, mock_time):
        student = MagicMock()
        student.email = 'test@example.com'
        student.name = 'Rodrigo de los tests'
        student.scores = '{"asm-badge":100}'
        AssessmentCertificates.\
            issue_certificates_by_assessment(
                student, 'asm-badge', 'specific')

        badges = Badges.get_badges_of_student(student.email)
        self.assertEqual(len(badges), 2)
        sents = SentBadge.all()
        sents = [sent for sent in sents]
        self.assertEqual(len(sents), 2)

    @patch.object(Badges, 'deferred_send_badge')
    @patch.object(Assessments, 'find_unit_by_id', return_value=_ASM_1)
    @patch.object(
        AssessmentCertificateDTO,
        'get_now',
        return_value=datetime.datetime(2017, 1, 14))
    def test_give_badge_permanent_half(
            self, mock_taskqueue, mock_assessment, mock_time):
        student = MagicMock()
        student.email = 'test@example.com'
        student.name = 'Rodrigo de los tests'
        student.scores = '{"asm-badge":100}'
        AssessmentCertificates.\
            issue_certificates_by_assessment(
                student, 'asm-badge', 'not-exist')

        badges = Badges.get_badges_of_student(student.email)
        self.assertEqual(len(badges), 1)
        sents = SentBadge.all()
        sents = [sent for sent in sents]
        self.assertEqual(len(sents), 1)
