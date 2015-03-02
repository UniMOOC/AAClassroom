import datetime
import json

from functional import actions

from modules.um_certificates.model import AssessmentCertificate


class AssessmentCertificateE2ETest(actions.TestBase):

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
        super(AssessmentCertificateE2ETest, self).setUp()
        for cert in self._CERT_LIST:
            cert.put()
        actions.login('test@example.com', True)

    def test_get_all(self):
        response = self.get('api/certificates')
        data = json.loads(response.body)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['count'], len(self._CERT_LIST))
        self.assertEqual(len(data['data']), len(self._CERT_LIST))

    def test_retrieve(self):
        response = self.get('api/certificates?id=' +
                            str(self._CERT_A.key().id()))
        data = json.loads(response.body)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['assessments'][0], 'asm1')
        self.assertEqual(data['badge'], 'A')

    def test_retrieve_not_exist(self):
        response = self.get(
            url='api/certificates?id=' + '123123123',
            expect_errors=True)
        self.assertEqual(response.status_code, 404)

    def test_create(self):
        obj = {
            'badge_id': 'A',
            'assessments': ['asm1'],
            'edition': 'new-edition',
            'date_start': '2015-12-21 10:39:43.070580',
            'date_end': '2015-12-23 10:39:43.070580'
        }
        resp = self.testapp.post_json(
            '/api/certificates',
            obj,
            expect_errors=True)
        self.assertEqual(resp.status_code, 200)
        obj_resp = json.loads(resp.body)
        self.assertEqual(obj_resp['edition'], obj['edition'])
        self.assertEqual(obj_resp['assessments'], obj['assessments'])
        self.assertEqual(obj_resp['badge'], obj['badge_id'])

    def test_update(self):
        new_asm = {
            'badge_id': 'A',
            'assessments': ['asm1'],
            'edition': 'new-edition',
            'date_start': '2015-12-21 10:39:43.070580',
            'date_end': '2015-12-23 10:39:43.070580'
        }
        resp = self.testapp.post_json(
            '/api/certificates?id=' + str(self._CERT_A.key().id()),
            new_asm,
            expect_errors=True)
        data = json.loads(resp.body)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data['edition'], new_asm['edition'])
        self.assertEqual(data['assessments'], new_asm['assessments'])
        self.assertEqual(data['badge'], new_asm['badge_id'])
        self.assertEqual(data['date_start'], new_asm['date_start'])
        self.assertEqual(data['date_end'], new_asm['date_end'])

        response = self.get('api/certificates?id=' +
                            str(self._CERT_A.key().id()))
        data = json.loads(response.body)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data['edition'], new_asm['edition'])
        self.assertEqual(data['assessments'], new_asm['assessments'])
        self.assertEqual(data['badge'], new_asm['badge_id'])
        self.assertEqual(data['date_start'], new_asm['date_start'])
        self.assertEqual(data['date_end'], new_asm['date_end'])

    def test_delete(self):
        id_to_test = str(self._CERT_A.key().id())
        response = self.get('api/certificates?id=' + id_to_test)
        self.assertEqual(response.status_code, 200)
        response = self.delete('api/certificates?id=' + id_to_test)
        self.assertEqual(response.status_code, 200)
        response = self.get(
            'api/certificates?id=' + id_to_test,
            expect_errors=True)
        self.assertEqual(response.status_code, 404)
