from django.core.management.base import BaseCommand
from exams.models import Question, Choice

class Command(BaseCommand):
    help = 'Creates sample questions for Eiken Grade 4'

    def handle(self, *args, **options):
        # 大問1: 文法空所補充の問題
        grammar_questions = [
            {
                'text': "I (    ) to school every day.",
                'choices': [
                    "go",
                    "goes",
                    "going",
                    "went"
                ],
                'correct_index': 0,
                'explanation': "主語が'I'なので、動詞は原形の'go'を使います。"
            },
            {
                'text': "She (    ) a book yesterday.",
                'choices': [
                    "read",
                    "reads",
                    "reading",
                    "readed"
                ],
                'correct_index': 0,
                'explanation': "過去形の文なので、動詞の過去形'read'を使います。"
            }
        ]

        # 大問2: 会話文空所補充の問題
        conversation_questions = [
            {
                'text': """
                A: How are you?
                B: (    )
                A: I'm fine, thank you.
                """,
                'choices': [
                    "I'm fine, thank you.",
                    "How are you?",
                    "Nice to meet you.",
                    "Good morning."
                ],
                'correct_index': 1,
                'explanation': "会話の流れに合わせて、'How are you?'と返すのが自然です。"
            },
            {
                'text': """
                A: What time is it?
                B: (    )
                """,
                'choices': [
                    "It's 3 o'clock.",
                    "I'm fine.",
                    "Thank you.",
                    "Yes, it is."
                ],
                'correct_index': 0,
                'explanation': "時間を尋ねられたので、具体的な時間を答えます。"
            }
        ]

        # 大問3: 語句整序の問題
        word_order_questions = [
            {
                'text': "次の語句を並び替えて正しい英文を作りなさい。\n\n(1) go (2) to (3) I (4) school",
                'choices': [
                    "3-1-2-4",
                    "1-2-3-4",
                    "3-4-1-2",
                    "4-1-2-3"
                ],
                'correct_index': 0,
                'explanation': "主語(I) + 動詞(go) + 前置詞(to) + 名詞(school)の順になります。"
            },
            {
                'text': "次の語句を並び替えて正しい英文を作りなさい。\n\n(1) a (2) book (3) reading (4) is (5) She",
                'choices': [
                    "5-4-3-1-2",
                    "3-4-5-1-2",
                    "5-1-2-3-4",
                    "1-2-3-4-5"
                ],
                'correct_index': 0,
                'explanation': "主語(She) + 動詞(is) + 現在分詞(reading) + 冠詞(a) + 名詞(book)の順になります。"
            }
        ]

        # 大問4: 長文読解の問題
        reading_questions = [
            {
                'text': """
                Tom is a student. He goes to school every day. His school is big and has many students. 
                Tom likes English and math. He studies hard every day.
                
                Q: What does Tom like?
                """,
                'choices': [
                    "English and math",
                    "Science and history",
                    "Music and art",
                    "Sports and games"
                ],
                'correct_index': 0,
                'explanation': "本文の'Tom likes English and math.'から、正解は'English and math'です。"
            },
            {
                'text': """
                Mary has a cat. Its name is Tama. Tama is white and very cute. 
                Mary plays with Tama every day after school.
                
                Q: What color is Tama?
                """,
                'choices': [
                    "White",
                    "Black",
                    "Brown",
                    "Gray"
                ],
                'correct_index': 0,
                'explanation': "本文の'Tama is white and very cute.'から、正解は'White'です。"
            }
        ]

        # リスニング第1部: 応答選択
        listening_response_questions = [
            {
                'text': "音声を聞いて、適切な応答を選びなさい。",
                'listening_text': "How are you today?",
                'choices': [
                    "I'm fine, thank you.",
                    "I'm 12 years old.",
                    "I like soccer."
                ],
                'correct_index': 0,
                'explanation': "'How are you?'に対する適切な応答は'I'm fine, thank you.'です。"
            },
            {
                'text': "音声を聞いて、適切な応答を選びなさい。",
                'listening_text': "What time is it now?",
                'choices': [
                    "It's 3:30.",
                    "It's Monday.",
                    "It's sunny."
                ],
                'correct_index': 0,
                'explanation': "時間を尋ねられたので、具体的な時間を答えます。"
            }
        ]

        # リスニング第2部: 会話内容一致
        listening_conversation_questions = [
            {
                'question_text': 'What are they talking about?',
                'listening_text': 'Do you have any plans for the weekend?\nI\'m going to visit my grandparents.',
                'choices': [
                    'Weekend plans',
                    'School work',
                    'Sports activities',
                    'Movie watching'
                ],
                'correct_choice': 0,
                'explanation': 'The conversation is about weekend plans, specifically visiting grandparents.'
            },
            {
                'question_text': 'Where does the conversation take place?',
                'listening_text': 'Can I help you find something?\nYes, I\'m looking for a birthday present for my sister.',
                'choices': [
                    'At a store',
                    'At a school',
                    'At a park',
                    'At a restaurant'
                ],
                'correct_choice': 0,
                'explanation': 'The conversation takes place at a store, as indicated by the offer to help find something.'
            }
        ]

        # リスニング第3部: 短文内容一致
        listening_short_passage_questions = [
            {
                'text': "音声を聞いて、内容に一致するものを選びなさい。",
                'listening_text': "Tom is a student. He goes to school by bus every day. His school starts at 8:30. He likes math and science.",
                'choices': [
                    "Tom goes to school by bus.",
                    "Tom walks to school.",
                    "Tom rides a bike to school."
                ],
                'correct_index': 0,
                'explanation': "音声の中で'goes to school by bus'と言っているので、正解は'Tom goes to school by bus.'です。"
            },
            {
                'text': "音声を聞いて、内容に一致するものを選びなさい。",
                'listening_text': "Mary has a cat. Its name is Tama. Tama is 3 years old. It likes to play with a ball.",
                'choices': [
                    "Tama is 3 years old.",
                    "Tama is 5 years old.",
                    "Tama is 1 year old."
                ],
                'correct_index': 0,
                'explanation': "音声の中で'Tama is 3 years old'と言っているので、正解は'Tama is 3 years old.'です。"
            }
        ]

        # 既存の問題を削除
        Question.objects.all().delete()

        # 大問1の問題を作成
        for i, q in enumerate(grammar_questions):
            question = Question.objects.create(
                question_text=q['text'],
                level=4,
                question_type='grammar_fill',
                explanation=q['explanation']
            )
            
            for j, choice_text in enumerate(q['choices']):
                Choice.objects.create(
                    question=question,
                    choice_text=choice_text,
                    is_correct=(j == q['correct_index'])
                )
            
            self.stdout.write(self.style.SUCCESS(f'Created grammar question {i+1}'))

        # 大問2の問題を作成
        for i, q in enumerate(conversation_questions):
            question = Question.objects.create(
                question_text=q['text'],
                level=4,
                question_type='conversation_fill',
                explanation=q['explanation']
            )
            
            for j, choice_text in enumerate(q['choices']):
                Choice.objects.create(
                    question=question,
                    choice_text=choice_text,
                    is_correct=(j == q['correct_index'])
                )
            
            self.stdout.write(self.style.SUCCESS(f'Created conversation question {i+1}'))

        # 大問3の問題を作成
        for i, q in enumerate(word_order_questions):
            question = Question.objects.create(
                question_text=q['text'],
                level=4,
                question_type='word_order',
                explanation=q['explanation']
            )
            
            for j, choice_text in enumerate(q['choices']):
                Choice.objects.create(
                    question=question,
                    choice_text=choice_text,
                    is_correct=(j == q['correct_index'])
                )
            
            self.stdout.write(self.style.SUCCESS(f'Created word order question {i+1}'))

        # 大問4の問題を作成
        for i, q in enumerate(reading_questions):
            question = Question.objects.create(
                question_text=q['text'],
                level=4,
                question_type='reading_comprehension',
                explanation=q['explanation']
            )
            
            for j, choice_text in enumerate(q['choices']):
                Choice.objects.create(
                    question=question,
                    choice_text=choice_text,
                    is_correct=(j == q['correct_index'])
                )
            
            self.stdout.write(self.style.SUCCESS(f'Created reading comprehension question {i+1}'))

        # リスニング第1部の問題を作成
        for i, q in enumerate(listening_response_questions):
            question = Question.objects.create(
                question_text=q['text'],
                level=4,
                question_type='listening_response',
                listening_text=q['listening_text'],
                explanation=q['explanation']
            )
            
            for j, choice_text in enumerate(q['choices']):
                Choice.objects.create(
                    question=question,
                    choice_text=choice_text,
                    is_correct=(j == q['correct_index'])
                )
            
            self.stdout.write(self.style.SUCCESS(f'Created listening response question {i+1}'))

        # リスニング第2部の問題を作成
        for i, q in enumerate(listening_conversation_questions):
            question = Question.objects.create(
                question_text=q['question_text'],
                level=4,
                question_type='listening_conversation',
                listening_text=q['listening_text'],
                explanation=q['explanation']
            )
            
            for j, choice_text in enumerate(q['choices']):
                Choice.objects.create(
                    question=question,
                    choice_text=choice_text,
                    is_correct=(j == q['correct_choice'])
                )
            
            self.stdout.write(self.style.SUCCESS(f'Created listening conversation question {i+1}'))

        # リスニング第3部の問題を作成
        for i, q in enumerate(listening_short_passage_questions):
            question = Question.objects.create(
                question_text=q['text'],
                level=4,
                question_type='listening_short_passage',
                listening_text=q['listening_text'],
                explanation=q['explanation']
            )
            
            for j, choice_text in enumerate(q['choices']):
                Choice.objects.create(
                    question=question,
                    choice_text=choice_text,
                    is_correct=(j == q['correct_index'])
                )
            
            self.stdout.write(self.style.SUCCESS(f'Created listening short passage question {i+1}'))

        self.stdout.write(self.style.SUCCESS('Successfully created sample questions')) 