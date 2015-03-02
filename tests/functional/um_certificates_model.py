import datetime

from functional import actions
from mock import patch

from modules.um_certificates.model import\
    AssessmentCertificate, AssessmentCertificateDAO, AssessmentCertificateDTO


class AssessmentCertificateDAOTest(actions.TestBase):

    _CERT_A = AssessmentCertificate(
        badge_id='A',
        assessments=['asm1'],
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
        badge_id='A',
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

    _CERT_LIST = [_CERT_A, _CERT_B, _CERT_C, _CERT_D, _CERT_E, _CERT_F,
                  _CERT_G, _CERT_H]

    def setUp(self):
        super(AssessmentCertificateDAOTest, self).setUp()
        for cert in self._CERT_LIST:
            cert.put()

    def test_create_get_and_set(self):
        AssessmentCertificateDAO.create(
            'A',
            ['asm-create'],
            'alicante')
        certs = AssessmentCertificateDAO.get_by_assessment_in_edition(
            'asm-create', 'alicante')
        self.assertEqual(len(certs), 1)
        certs[0].edition = 'galicia'
        AssessmentCertificateDAO.set(certs[0])
        certs = AssessmentCertificateDAO.get_by_assessment_in_edition(
            'asm-create', 'galicia')
        self.assertEqual(len(certs), 1)
        certs = AssessmentCertificateDAO.get_by_assessment_in_edition(
            'asm-create', 'alicante')
        self.assertEqual(len(certs), 0)

    def test_get_all(self):
        certs = AssessmentCertificateDAO.all_in_edition('alicante')
        self.assertEqual(len(certs), 7)
        certs = AssessmentCertificateDAO.all_in_edition('barcelona')
        self.assertEqual(len(certs), 1)

    def test_for_assessment(self):
        certs = AssessmentCertificateDAO.get_by_assessment_in_edition(
            'asm1', 'alicante')
        self.assertEqual(len(certs), 3)
        certs = AssessmentCertificateDAO.get_by_assessment_in_edition(
            'asm2', 'alicante')
        self.assertEqual(len(certs), 1)
        certs = AssessmentCertificateDAO.get_by_assessment_in_edition(
            'asm-final', 'barcelona')
        self.assertEqual(len(certs), 1)

    def test_for_assessment_not_exist(self):
        certs = AssessmentCertificateDAO.get_by_assessment_in_edition(
            'asm-inexistent', 'alicante')
        self.assertEqual(len(certs), 0)
        certs = AssessmentCertificateDAO.get_by_assessment_in_edition(
            'asm1', 'not-existent')
        self.assertEqual(len(certs), 0)
        certs = AssessmentCertificateDAO.get_by_assessment_in_edition(
            'asm-inexistent', 'not-existent')
        self.assertEqual(len(certs), 0)

    @patch.object(
        AssessmentCertificateDTO,
        'get_now',
        return_value=datetime.datetime(2015, 1, 14))
    def test_get_actives(self, mock_datetime):
        certs = AssessmentCertificateDAO.get_actives_in_edition('alicante')
        self.assertEqual(len(certs), 4)
        certs = AssessmentCertificateDAO.get_actives_in_edition('barcelona')
        self.assertEqual(len(certs), 0)

    @patch.object(
        AssessmentCertificateDTO,
        'get_now',
        return_value=datetime.datetime(2015, 1, 14))
    def test_get_actives_by_assessment_in_edition(self, mock_datetime):
        certs = AssessmentCertificateDAO.get_actives_by_assessment_in_edition(
            'asm1', 'alicante')
        self.assertEqual(len(certs), 2)
        certs = AssessmentCertificateDAO.get_actives_by_assessment_in_edition(
            'asm3', 'alicante')
        self.assertEqual(len(certs), 2)
        certs = AssessmentCertificateDAO.get_actives_by_assessment_in_edition(
            'asm2', 'alicante')
        self.assertEqual(len(certs), 0)
