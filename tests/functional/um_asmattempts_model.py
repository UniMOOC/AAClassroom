
from functional import actions

from modules.um_assessments.model import AsmAttemptsDAO


EMAIL = 'test@example.com'
ATT = {'test': 'test'}


class AsmAttemptsDAOTest(actions.TestBase):

    def test_create(self):
        asm_att = AsmAttemptsDAO.create(EMAIL, ATT)
        self.assertIsNotNone(asm_att)
        self.assertEqual(asm_att.attempts_left, ATT)

    def test_create_and_get(self):
        AsmAttemptsDAO.create(EMAIL, ATT)
        asm_att = AsmAttemptsDAO.get(EMAIL)
        self.assertIsNotNone(asm_att)
        self.assertEqual(asm_att.attempts_left, ATT)

    def test_create_set_and_get(self):
        asm_att = AsmAttemptsDAO.create(EMAIL, ATT)
        new_att = {'test': 'example'}
        asm_att.attempts_left = new_att
        AsmAttemptsDAO.set(asm_att)
        asm_att = AsmAttemptsDAO.get(EMAIL)
        self.assertIsNotNone(asm_att)
        self.assertEqual(asm_att.attempts_left, new_att)
