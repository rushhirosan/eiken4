from django.test import SimpleTestCase

from exams.answer_keys import (
    KIND_LISTENING,
    KIND_QUESTION,
    KIND_READING,
    answer_field_name,
    decode_session_ref,
    encode_session_ref,
    ids_for_kind,
    iter_submitted_answers,
    kind_for_model_instance,
)


class AnswerKeysTests(SimpleTestCase):
    def test_typed_field_names(self):
        self.assertEqual(answer_field_name(KIND_QUESTION, 12), 'answer_q_12')
        self.assertEqual(answer_field_name(KIND_LISTENING, 12), 'answer_lq_12')
        self.assertEqual(answer_field_name(KIND_READING, 12), 'answer_rq_12')

    def test_iter_submitted_answers_prefers_typed_keys(self):
        post = {
            'answer_q_1': '10',
            'answer_lq_1': '3',
            'answer_1': 'should-ignore-without-default',
            'csrfmiddlewaretoken': 'x',
        }
        rows = iter_submitted_answers(post)
        self.assertEqual(
            sorted(rows),
            sorted([
                (KIND_QUESTION, 1, '10'),
                (KIND_LISTENING, 1, '3'),
            ]),
        )

    def test_legacy_keys_only_with_default_kind(self):
        post = {'answer_5': '2'}
        self.assertEqual(iter_submitted_answers(post), [])
        self.assertEqual(
            iter_submitted_answers(post, default_kind=KIND_LISTENING),
            [(KIND_LISTENING, 5, '2')],
        )

    def test_session_ref_roundtrip(self):
        ref = encode_session_ref(KIND_LISTENING, 21)
        self.assertEqual(decode_session_ref(ref), (KIND_LISTENING, 21))
        self.assertIsNone(decode_session_ref(21))
        self.assertIsNone(decode_session_ref('21'))

    def test_kind_for_model_instance_by_class_name(self):
        class ListeningQuestion:
            id = 1

        class Question:
            id = 2

        self.assertEqual(kind_for_model_instance(ListeningQuestion()), KIND_LISTENING)
        self.assertEqual(kind_for_model_instance(Question()), KIND_QUESTION)

    def test_ids_for_kind(self):
        subs = [
            (KIND_QUESTION, 1, 'a'),
            (KIND_LISTENING, 2, 'b'),
            (KIND_QUESTION, 3, 'c'),
        ]
        self.assertEqual(ids_for_kind(subs, KIND_QUESTION), [1, 3])
