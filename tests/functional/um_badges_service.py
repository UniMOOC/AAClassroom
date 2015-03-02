import datetime
from functional import actions
from modules.um_badges.model import SentBadge
from modules.um_badges.service import Badges, OpenBadges


class BadgesTest(actions.TestBase):

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
        status='PENDING')

    _SENT_BADGE_C = SentBadge(
        name='B',
        badge='C',
        email='b@b.com',
        issued_on=datetime.datetime.strptime(
            '2013-12-14 10:39:46.890870', "%Y-%m-%d %H:%M:%S.%f"),
        status='ALREADY_SENT')

    _SENT_BADGE_D = SentBadge(
        name='B',
        badge='C',
        email='b@b.com',
        issued_on=datetime.datetime.strptime(
            '2013-12-13 10:39:46.890870', "%Y-%m-%d %H:%M:%S.%f"),
        status='SENT')

    _SENT_BADGE_E = SentBadge(
        name='C',
        badge='C',
        email='c@c.com',
        issued_on=datetime.datetime.strptime(
            '2013-12-13 10:39:46.890870', "%Y-%m-%d %H:%M:%S.%f"),
        status='SENT')

    _SENT_BADGES_LIST = [_SENT_BADGE_A, _SENT_BADGE_B, _SENT_BADGE_C,
                         _SENT_BADGE_D, _SENT_BADGE_E]

    def setUp(self):
        super(BadgesTest, self).setUp()
        self._store_badges_in_db()

    def _store_badges_in_db(self):
        for badge in self._SENT_BADGES_LIST:
            badge.put()

    def test_a_give_badge(self):
        email = 'b@b.com'
        badge_id = 'A'
        name = 'Mr B'
        self.assertFalse(Badges.student_has_badge(
            email, badge_id))
        Badges.give_badge(email, name, badge_id)
        self.assertTrue(Badges.student_has_badge(
            email, badge_id))

    def test_get_badge_of_student(self):
        badge = Badges.get_badge_of_student('b@b.com', 'C')
        self.assertEqual(badge, 'C')
        badge = Badges.get_badge_of_student('b@b.com', 'B')
        self.assertEqual(badge, 'B')
        badge = Badges.get_badge_of_student('b@b.com', 'A')
        self.assertIsNone(badge)

    def test_student_has_badge(self):
        self.assertTrue(Badges.student_has_badge('b@b.com', 'C'))
        self.assertTrue(Badges.student_has_badge('b@b.com', 'B'))
        self.assertFalse(Badges.student_has_badge('b@b.com', 'A'))

    def test_mails_with_badge(self):
        mails = Badges.get_mails_with_badge('B')
        self.assertEqual(len(mails), 1)
        mails = Badges.get_mails_with_badge('C')
        self.assertEqual(len(mails), 2)

    def test_get_pending_sent_badges(self):
        pending = Badges.get_pending()
        self.assertEqual(len(pending), 2)

    def test_get_badges_of_student(self):
        badges = Badges.get_badges_of_student('b@b.com')
        self.assertEqual(len(badges), 2)


class OpenBadgesTest(actions.TestBase):
    def test_get_config(self):
        config = OpenBadges.CONFIG['openbadges']
        self.assertIsNotNone(config)
        self.assertIsNotNone(config['api_host'])
