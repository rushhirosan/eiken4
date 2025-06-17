from django.core.management.base import BaseCommand
from exams.models import Question, Choice
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'listening_illustration_questions.txt からイラスト問題を登録する'

    def handle(self, *args, **options):
        try:
            file_path = os.path.join(settings.BASE_DIR, 'questions', 'listening_illustration_questions.txt')
            if not os.path.exists(file_path):
                self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
                return

            self.stdout.write(f'Reading file: {file_path}')
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                # 問題番号で分割
                blocks = []
                current_block = []
                for line in content.split('\n'):
                    if line.strip().startswith('No.'):
                        if current_block:
                            blocks.append('\n'.join(current_block))
                        current_block = [line]
                    else:
                        current_block.append(line)
                if current_block:
                    blocks.append('\n'.join(current_block))

            self.stdout.write(f'Found {len(blocks)} blocks')

            for block_num, block in enumerate(blocks):
                self.stdout.write(f'--- Block {block_num+1} ---')
                lines = [l for l in block.split('\n') if l.strip()]
                if not lines:
                    continue
                question_number = lines[0].strip()
                self.stdout.write(f'Processing question {question_number}')
                choices = []
                correct_answer = None
                explanation = []
                in_explanation = False
                next_line_is_answer = False

                for line in lines[1:]:
                    self.stdout.write(f'Line: {repr(line)}')
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith('【正解'):
                        next_line_is_answer = True
                        continue
                    if next_line_is_answer:
                        correct_answer = line
                        self.stdout.write(f'正解: {repr(correct_answer)}')
                        next_line_is_answer = False
                        continue
                    if line.startswith('【解説'):
                        in_explanation = True
                        continue
                    if in_explanation:
                        explanation.append(line)
                        continue
                    if line[0].isdigit() and line[1:3] == '. ':
                        choices.append(line)
                        self.stdout.write(f'選択肢: {repr(line)}')
                        continue

                if not correct_answer:
                    self.stdout.write(self.style.ERROR('No correct answer found in block'))
                    continue

                # 問題文を選択肢のみの形式に変更
                choices_text = '\n'.join(choices)
                question_text = f"Question.1\n{choices_text}"
                try:
                    correct_index = int(correct_answer.split('.')[0]) - 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'正解インデックス取得エラー: {str(e)} correct_answer={repr(correct_answer)}'))
                    continue
                explanation_text = '\n'.join(explanation)
                question = Question.objects.create(
                    question_text=question_text,
                    level='4',
                    question_type='listening_illustration',
                    explanation=explanation_text,
                    listening_text='',
                    image=None
                )
                for i, choice_text in enumerate(choices):
                    choice_text = choice_text.split('. ', 1)[1]
                    Choice.objects.create(
                        question=question,
                        choice_text=choice_text,
                        is_correct=(i == correct_index),
                        order=i
                    )
                self.stdout.write(self.style.SUCCESS(f'Successfully created listening illustration question {question_number}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}')) 