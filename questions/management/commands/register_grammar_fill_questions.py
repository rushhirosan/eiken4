from django.core.management.base import BaseCommand
from exams.models import Question, Choice
import re

class Command(BaseCommand):
    help = 'Register all grammar fill questions (1-165) from text file'

    def handle(self, *args, **options):
        # Clear all existing grammar fill questions
        Question.objects.filter(question_type='grammar_fill').delete()
        self.stdout.write(self.style.WARNING('既存の文法語彙問題をすべて削除しました'))
        
        # Read the text file
        with open('data/questions/grammar_fill_questions.txt', 'r', encoding='utf-8') as file:
            content = file.read()

        # Split into questions
        questions = content.split('---')
        
        registered_count = 0
        for question_block in questions:
            if not question_block.strip():
                continue

            try:
                # Extract question number
                question_number_match = re.search(r'問題(\d+):', question_block)
                if not question_number_match:
                    continue
                question_number = int(question_number_match.group(1))
                
                # Process all questions (1-165)
                if question_number < 1 or question_number > 165:
                    continue

                # Extract question text
                question_match = re.search(r'問題\d+:\s*(.*?)\s*選択肢\d+:', question_block, re.DOTALL)
                if not question_match:
                    continue
                question_text = question_match.group(1).strip()

                # Extract choices
                choices_match = re.search(r'選択肢\d+:\s*(.*?)\s*【正解\d+】', question_block, re.DOTALL)
                if not choices_match:
                    continue
                choices_text = choices_match.group(1).strip()
                
                # Parse choices properly
                choices = []
                for line in choices_text.split('\n'):
                    line = line.strip()
                    if re.match(r'^\d+\.', line):
                        # Extract choice text after the number
                        choice_text = re.sub(r'^\d+\.\s*', '', line)
                        choices.append(choice_text)

                # Extract correct answer number and text
                correct_match = re.search(r'【正解\d+】\s*(\d+)\.\s*(.*?)\s*【解説\d+】', question_block, re.DOTALL)
                if not correct_match:
                    continue
                correct_answer_number = int(correct_match.group(1))
                correct_answer_text = correct_match.group(2).strip()

                # Extract explanation
                explanation_match = re.search(r'【解説\d+】\s*(.*?)(?=\n\n|$)', question_block, re.DOTALL)
                explanation = explanation_match.group(1).strip() if explanation_match else ''

                # Create question
                question = Question.objects.create(
                    question_text=question_text,
                    level='4',  # Default to Grade 4
                    question_type='grammar_fill',
                    question_number=question_number,
                    explanation=explanation
                )

                # Create choices
                for order, choice_text in enumerate(choices, 1):
                    is_correct = (order == correct_answer_number)
                    Choice.objects.create(
                        question=question,
                        choice_text=choice_text,
                        is_correct=is_correct,
                        order=order
                    )

                registered_count += 1
                self.stdout.write(self.style.SUCCESS(f'問題{question_number}を登録しました: {question_text[:50]}...'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'問題{question_number}の登録でエラー: {str(e)}'))
                continue

        self.stdout.write(self.style.SUCCESS(f'\n登録完了: {registered_count}問の問題を登録しました'))
        
        # 確認
        total_questions = Question.objects.filter(question_type='grammar_fill').count()
        self.stdout.write(self.style.SUCCESS(f'データベース内の文法語彙問題総数: {total_questions}問')) 