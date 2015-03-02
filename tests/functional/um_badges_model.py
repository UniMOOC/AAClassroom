import datetime

from functional import actions
from modules.um_badges.model import\
    SentBadgeDAO, SentBadge, SentBadgeDTO


class SentBadgeDAOTest(actions.TestBase):
    _SENT_BADGE_A = SentBadge(
        name='A',
        badge='A',
        email='a@a.com',
        issued_on=datetime.datetime.strptime(
            '2012-12-13 10:39:43.070580', "%Y-%m-%d %H:%M:%S.%f"),
        status='PENDING')

    _SENT_BADGE_B = SentBadge(
        name='B',
        badge='B',
        email='b@b.com',
        issued_on=datetime.datetime.strptime(
            '2014-12-14 10:39:46.890870', "%Y-%m-%d %H:%M:%S.%f"),
        status='ALREADY_SENT')

    _SENT_BADGES_LIST = [_SENT_BADGE_A, _SENT_BADGE_B]

    _USER_A = {'email': 'test@example.com', 'name': 'Tester'}

    def setUp(self):
        super(SentBadgeDAOTest, self).setUp()
        self._store_sent_badges_in_db()

    def _store_sent_badges_in_db(self):
        for badge in self._SENT_BADGES_LIST:
            badge.put()

    def test_get_all(self):
        badges = SentBadgeDAO.get()
        self.assertEqual(len(self._SENT_BADGES_LIST), len(badges))

    def test_get_status_PENDING(self):
        badges = SentBadgeDAO.get_before(status='PENDING')
        self.assertEqual(1, len(badges))

    def test_get_before_all(self):
        date_before = datetime.datetime.strptime(
            '2011-12-13 10:39:43.070580', "%Y-%m-%d %H:%M:%S.%f")
        badges = SentBadgeDAO.get_before(issued_on=date_before)
        self.assertEqual(len(self._SENT_BADGES_LIST), len(badges))

    def test_get_before_2013(self):
        date_before = datetime.datetime.strptime(
            '2013-01-01 00:39:43.070580', "%Y-%m-%d %H:%M:%S.%f")
        badges = SentBadgeDAO.get_before(issued_on=date_before)
        self.assertEqual(1, len(badges))

    def test_create_get_set_and_get(self):
        badge_to_sent = 'A'
        SentBadgeDAO.create(
            self._USER_A['email'],
            self._USER_A['name'],
            badge_to_sent)

        badge_retrieved = SentBadgeDAO.get(
            user_email=self._USER_A['email'],
            badge_id=badge_to_sent,
            single_record=True)

        self.assertIsNotNone(badge_retrieved)

        badge_dto = SentBadgeDTO()
        badge_dto.user_email = self._USER_A['email']
        badge_dto.badge_id = badge_to_sent
        badge_dto.status = 'SENT'
        SentBadgeDAO.set(badge_dto)

        badge_retrieved = SentBadgeDAO.get(
            user_email=self._USER_A['email'],
            badge_id=badge_to_sent,
            single_record=True)

        self.assertEqual(badge_retrieved.status, 'SENT')

    def test_get_of_student(self):
        badge = SentBadgeDAO.get(
            user_email='b@b.com', badge_id='B', single_record=True)
        self.assertIsNotNone(badge)

    def test_get_of_student_not_exist(self):
        badge = SentBadgeDAO.get(
            user_email='b@b.com', badge_id='D', single_record=True)
        self.assertIsNone(badge)
