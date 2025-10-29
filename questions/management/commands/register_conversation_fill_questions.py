from django.core.management.base import BaseCommand
from exams.models import Question, Choice
import re

class Command(BaseCommand):
    help = 'Register all conversation fill questions (1-55) from text file'

    def handle(self, *args, **options):
        # Clear all existing conversation fill questions
        Question.objects.filter(
            question_type='conversation_fill'
        ).delete()
        self.stdout.write(self.style.WARNING('既存の会話穴埋め問題をすべて削除しました'))
        
        # Read the text file
        with open('data/questions/conversation_questions.txt', 'r', encoding='utf-8') as file:
            content = file.read()

        # Split into questions
        questions = content.split('---')
        
        registered_count = 0
        for question_block in questions:
            if not question_block.strip():
                continue

            try:
                # Extract question number (handle cases like "問題21（改善版）:")
                question_number_match = re.search(r'問題(\d+)', question_block)
                if not question_number_match:
                    continue
                question_number = int(question_number_match.group(1))
                
                # Process questions 1-55
                if question_number < 1 or question_number > 55:
                    continue

                # Extract question text (handle cases like "問題21（改善版）:")
                question_match = re.search(r'問題\d+[^:]*:\s*(.*?)\s*選択肢\d+:', question_block, re.DOTALL)
                if not question_match:
                    self.stdout.write(self.style.WARNING(f'Could not extract question text from question {question_number}'))
                    continue
                question_text = question_match.group(1).strip()

                # Extract choices
                choices_match = re.search(r'選択肢\d+:\s*(.*?)\s*【正解\d+】', question_block, re.DOTALL)
                if not choices_match:
                    self.stdout.write(self.style.WARNING(f'Could not extract choices from question {question_number}'))
                    continue
                choices_text = choices_match.group(1).strip()
                # 選択肢を抽出（1.から4.まで。5.以降は除外）
                raw_choices = [c.strip() for c in choices_text.split('\n') if c.strip() and re.match(r'^[1-4]\.', c.strip())]
                
                # 重複チェック（数字を除去した内容でチェック）
                seen_texts = set()
                choices = []
                for c in raw_choices:
                    clean_text = re.sub(r'^\d+\.\s*', '', c.strip())
                    if clean_text not in seen_texts:
                        seen_texts.add(clean_text)
                        choices.append(c)
                    else:
                        self.stdout.write(self.style.WARNING(f'問題{question_number}: 重複選択肢を検出しました - {clean_text}'))
                
                # 選択肢が4個でない場合は警告
                if len(choices) != 4:
                    self.stdout.write(self.style.WARNING(f'問題{question_number}: 選択肢が{len(choices)}個です（4個であるべきです）'))

                # Extract correct answer
                correct_match = re.search(r'【正解\d+】\s*(.*?)\s*【解説\d+】', question_block, re.DOTALL)
                if not correct_match:
                    self.stdout.write(self.style.WARNING(f'Could not extract correct answer from question {question_number}'))
                    continue
                correct_answer = correct_match.group(1).strip()

                # Extract explanation
                explanation_match = re.search(r'【解説\d+】\s*(.*?)(?=\n\n|$)', question_block, re.DOTALL)
                explanation = explanation_match.group(1).strip() if explanation_match else ''

                # Create question
                question = Question.objects.create(
                    question_text=question_text,
                    level='4',  # Default to Grade 4
                    question_type='conversation_fill',
                    question_number=question_number,
                    explanation=explanation
                )

                # Create choices
                for order, choice_text in enumerate(choices, 1):
                    # Remove the number prefix (1., 2., etc.) for comparison
                    clean_choice = re.sub(r'^\d+\.\s*', '', choice_text.strip())
                    clean_correct = re.sub(r'^\d+\.\s*', '', correct_answer.strip())
                    is_correct = clean_choice == clean_correct
                    
                    Choice.objects.create(
                        question=question,
                        choice_text=clean_choice,
                        is_correct=is_correct,
                        order=order
                    )

                registered_count += 1
                self.stdout.write(self.style.SUCCESS(f'問題{question_number}を登録しました'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'問題{question_number}の登録でエラー: {str(e)}'))
                continue

        self.stdout.write(self.style.SUCCESS(f'\n登録完了: {registered_count}問の問題を登録しました'))
        
        # 確認
        total_questions = Question.objects.filter(question_type='conversation_fill').count()
        self.stdout.write(self.style.SUCCESS(f'データベース内の会話穴埋め問題総数: {total_questions}問')) 