from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from exams.provenance import PROVENANCE_ORIGINAL
from exams.models import Question
from questions.management.commands.register_speaking_questions import _parse_speaking_block

User = get_user_model()


class Pre2MenuTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='pre2user',
            email='pre2@example.com',
            password='testpass123',
        )
        self.client.login(username='pre2user', password='testpass123')

    def test_exam_list_shows_pre2_formats(self):
        response = self.client.get(reverse('exams:exam_list'), {'level': 'pre2'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '準2級（ベータ）')
        self.assertContains(response, 'ベータ公開です。問題はまだ改善中です。')
        self.assertContains(response, 'type=grammar_fill')
        self.assertContains(response, 'type=conversation_fill')
        self.assertContains(response, 'type=reading_comprehension')
        self.assertContains(response, 'type=writing')
        self.assertContains(response, 'type=listening_illustration')
        self.assertContains(response, '第1部: 会話の応答')
        self.assertContains(response, 'type=listening_conversation')
        self.assertContains(response, 'type=listening_passage')
        self.assertContains(response, 'type=speaking')
        self.assertNotContains(response, 'type=word_order')

    def test_listening_part1_page_title_matches_official_response_format(self):
        response = self.client.get(
            reverse('exams:question_list_by_level', kwargs={'level': 'pre2'}),
            {'type': 'listening_illustration'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'リスニング第1部: 会話の応答')
        self.assertNotContains(response, 'イラスト問題')

    def test_speaking_parser_turns_card_over_after_picture_questions(self):
        block = """
問題1:
【Title】
City Library Night

【Passage】
Once a month, the city library stays open until nine.

【Illustration】
Picture A: students with books. Picture B: a closed door.

【Questions】
1. [passage] How often does the library stay open late?
2. [illustration] What are the students doing?
3. [illustration] What is the situation?
4. [personal] Do you think libraries should stay open late?
   Yes: Why?
   No: Why not?
5. [personal] Do you read books on weekdays?
   Yes: What kind of books do you like?
   No: What do you like to do instead?

【参考解答】
1. Once a month.
"""
        _text, _explanation, data, _points = _parse_speaking_block(block, 1, 'pre2')
        self.assertEqual(data['turn_over_after'], 3)
        self.assertIsNone(data['aloud_seconds'])
        self.assertEqual(data['questions'][3]['yes_prompt'], 'Why?')
        self.assertEqual(data['questions'][4]['no_prompt'], 'What do you like to do instead?')
        Question.objects.create(
            provenance=PROVENANCE_ORIGINAL,
            question_text='City Library Night',
            question_type='speaking',
            level='pre2',
            question_number=1,
            speaking_data=data,
        )
        response = self.client.get(
            reverse('exams:question_list_by_level', kwargs={'level': 'pre2'}),
            {'type': 'speaking'},
        )
        self.assertContains(response, 'カードを裏返してください')
        self.assertContains(response, 'City Library Night')
