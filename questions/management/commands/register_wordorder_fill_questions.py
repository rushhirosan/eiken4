from django.core.management.base import BaseCommand
from exams.models import Question, Choice
import re

from exams.provenance import PROVENANCE_BLOCKED
from questions.legacy_import import assert_legacy_question_import_allowed
from questions.level_paths import (
    add_default_register_arguments,
    questions_file_abspath,
)


class Command(BaseCommand):
    help = 'Register all word order questions from data/questions/wordorder_questions.txt'

    def add_arguments(self, parser):
        add_default_register_arguments(parser)

    def handle(self, *args, **options):
        assert_legacy_question_import_allowed(allow_flag=options.get('allow_legacy_blocked_import', False))
        level = options['level']
        Question.objects.filter(question_type='word_order', level=level).delete()
        self.stdout.write(self.style.WARNING(f'既存の語順穴埋め問題（level={level}）を削除しました'))
        
        txt_path = questions_file_abspath(level, 'wordorder_questions.txt')
        with open(txt_path, 'r', encoding='utf-8') as file:
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
                
                # Extract question text (日本語文＋英語文)
                question_match = re.search(r'問題\d+:\s*(.*?)\n選択肢\d+:', question_block, re.DOTALL)
                if not question_match:
                    self.stdout.write(self.style.WARNING(f'Could not extract question text from question {question_number}'))
                    continue
                question_text = question_match.group(1).strip()

                # Extract choices
                choices_match = re.search(r'選択肢\d+:\s*(.*?)\n【正解\d+】', question_block, re.DOTALL)
                if not choices_match:
                    self.stdout.write(self.style.WARNING(f'Could not extract choices from question {question_number}'))
                    continue
                choices_text = choices_match.group(1).strip()
                choices = [c.strip() for c in choices_text.split('\n') if c.strip() and c.strip().startswith(('1.', '2.', '3.', '4.'))]

                # Extract correct answer
                correct_match = re.search(r'【正解\d+】\s*(.*?)\n【解説\d+】', question_block, re.DOTALL)
                if not correct_match:
                    self.stdout.write(self.style.WARNING(f'Could not extract correct answer from question {question_number}'))
                    continue
                correct_answer = correct_match.group(1).strip()

                # Extract explanation
                explanation_match = re.search(r'【解説\d+】\s*(.*?)(?=\n\n|$)', question_block, re.DOTALL)
                explanation = explanation_match.group(1).strip() if explanation_match else ''

                # Create question
                question = Question.objects.create(
                    provenance=PROVENANCE_BLOCKED,
                    question_text=question_text,
                    level=level,
                    question_type='word_order',
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
        total_questions = Question.objects.filter(
            question_type='word_order', level=level
        ).count()
        self.stdout.write(self.style.SUCCESS(f'データベース内の語順穴埋め問題総数（level={level}）: {total_questions}問')) 