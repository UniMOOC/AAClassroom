
from mock import patch
from mock import MagicMock

from functional import actions

from modules.um_course.service import Courses
from modules.um_assessments.service import Assessments


ASM = MagicMock(html_content='{"test": "test"}')
QUESTION_1 = [
    {"correct": 0, "key": 1, "options": ["V", "F"], "question": "V?"}
]
QUESTIONS_2 = [
    {"correct": 0, "key": 1, "options": ["V", "F"], "question": "V?"},
    {"correct": 1, "key": 2, "options": ["V", "F"], "question": "V?"}
]
QUESTIONS_3 = [
    {"correct": 1, "key": 1, "options": ["V", "F"], "question": "V?"},
    {"correct": 1, "key": 2, "options": ["V", "F"], "question": "V?"},
    {"correct": 0, "key": 3, "options": ["V", "F"], "question": "V?"}
]
ANSWER_1_PASS = {"1": 0}
ANSWER_1_FAIL = {"1": 1}
ANSWERS_2_PASS = {"1": 0, "2": 1}
ANSWERS_2_FAIL = {"1": 1, "2": 0}
ANSWERS_3_PASS = {"1": 1, "2": 1, "3": 0}
ANSWERS_3_FAIL = {"1": 0, "2": 0}


class AssessmentsTest(actions.TestBase):
    @patch.object(Courses, 'find_unit_by_id', return_value=None)
    def test_find_nonexistent(self, mock_find):
        unit_id = 1
        asm = Assessments.find_unit_by_id(unit_id)
        self.assertIsNone(asm)

    @patch.object(Courses, 'find_unit_by_id', return_value=ASM)
    def test_find_existent(self, mock_find):
        unit_id = 1
        asm = Assessments.find_unit_by_id(unit_id)
        self.assertEquals(asm.html_content, {'test': 'test'})

    def test_grade_1_q_passed(self):
        score, feedback = Assessments.grade(QUESTION_1, ANSWER_1_PASS)
        self.assertEquals(score, 100)
        self.assertEquals(len(feedback), 1)
        self.assertEquals(feedback[0]['type'], "correct")

    def test_grade_1_q_failed(self):
        score, feedback = Assessments.grade(QUESTION_1, ANSWER_1_FAIL)
        self.assertEquals(score, 0)
        self.assertEquals(len(feedback), 1)
        self.assertEquals(feedback[0]['type'], "wrong")

    def test_grade_2_q_passed(self):
        score, feedback = Assessments.grade(QUESTIONS_2, ANSWERS_2_PASS)
        self.assertEquals(score, 100)
        self.assertEquals(len(feedback), 2)
        self.assertEquals(feedback[0]['type'], "correct")
        self.assertEquals(feedback[1]['type'], "correct")

    def test_grade_2_q_failed(self):
        score, feedback = Assessments.grade(QUESTIONS_2, ANSWERS_2_FAIL)
        self.assertEquals(score, 0)
        self.assertEquals(len(feedback), 2)
        self.assertEquals(feedback[0]['type'], "wrong")
        self.assertEquals(feedback[1]['type'], "wrong")

    def test_grade_3_q_passed(self):
        score, feedback = Assessments.grade(QUESTIONS_3, ANSWERS_3_PASS)
        self.assertEquals(score, 100)
        self.assertEquals(len(feedback), 3)
        self.assertEquals(feedback[0]['type'], "correct")
        self.assertEquals(feedback[1]['type'], "correct")

    def test_grade_3_q_failed(self):
        score, feedback = Assessments.grade(QUESTIONS_3, ANSWERS_3_FAIL)
        self.assertEquals(score, 0)
        self.assertEquals(len(feedback), 3)
        self.assertEquals(feedback[0]['type'], "wrong")
        self.assertEquals(feedback[1]['type'], "wrong")
        self.assertEquals(feedback[2]['type'], "not_answered")

    def test_grade_and_update_w_scores_pass(self):
        STUDENT = MagicMock(put=MagicMock(), scores="{}")
        asm_id = 1
        score, feedback = Assessments.grade_and_update_score(
            QUESTIONS_3, ANSWERS_3_PASS, STUDENT, asm_id
        )

        self.assertEquals(STUDENT.scores, '{"1": 100.0}')
        STUDENT.put.assert_called_with()

    def test_grade_and_update_wout_scores_pass(self):
        STUDENT = MagicMock(put=MagicMock(), scores="")
        asm_id = 1
        score, feedback = Assessments.grade_and_update_score(
            QUESTIONS_3, ANSWERS_3_PASS, STUDENT, asm_id
        )

        self.assertEquals(STUDENT.scores, '{"1": 100.0}')
        STUDENT.put.assert_called_with()

    def test_grade_and_update_w_scores_fail(self):
        STUDENT = MagicMock(put=MagicMock(), scores="{}")
        asm_id = 1
        score, feedback = Assessments.grade_and_update_score(
            QUESTIONS_3, ANSWERS_3_FAIL, STUDENT, asm_id
        )

        self.assertEquals(STUDENT.scores, '{"1": 0.0}')
        STUDENT.put.assert_called_with()

    def test_grade_and_update_wout_scores_fail(self):
        STUDENT = MagicMock(put=MagicMock(), scores="")
        asm_id = 1
        score, feedback = Assessments.grade_and_update_score(
            QUESTIONS_3, ANSWERS_3_FAIL, STUDENT, asm_id
        )

        self.assertEquals(STUDENT.scores, '{"1": 0.0}')
        STUDENT.put.assert_called_with()
