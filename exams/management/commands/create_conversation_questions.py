from django.core.management.base import BaseCommand
from exams.models import Question, Choice
import re

class Command(BaseCommand):
    help = 'Create conversation questions from text file'

    def handle(self, *args, **options):
        # 既存の問題を削除
        Question.objects.filter(question_type='conversation_fill').delete()
        self.stdout.write('Deleted existing conversation questions')

        # テキストファイルを読み込む
        with open('questions/conversation_questions.txt', 'r', encoding='utf-8') as f:
            content = f.read()

        # 問題ごとに分割
        questions = re.split(r'\n---\n', content)

        for q_text in questions:
            if not q_text.strip():
                continue

            # 問題番号を取得
            question_num = int(re.search(r'問題(\d+)', q_text).group(1))
            
            # 問題文を抽出
            question_text = ''
            choices = []
            correct_answer = None
            explanation = ''
            
            lines = q_text.split('\n')
            current_section = 'question'
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('【正解'):
                    current_section = 'correct'
                    continue
                elif line.startswith('【解説'):
                    current_section = 'explanation'
                    continue
                elif line.startswith('選択肢'):
                    current_section = 'choices'
                    continue
                
                if current_section == 'question':
                    # 「問題24:」のような行を除外
                    if not line.startswith('問題') and ':' in line:
                        question_text += line + '\n'
                elif current_section == 'choices':
                    if line.startswith(('1.', '2.', '3.', '4.')):
                        choices.append(line[2:].strip())
                elif current_section == 'correct':
                    correct_answer = line
                    if correct_answer.startswith(('1.', '2.', '3.', '4.')):
                        correct_answer = correct_answer[2:].strip()
                elif current_section == 'explanation':
                    explanation += line + '\n'

            # 問題を作成
            question = Question.objects.create(
                level='4',  # 英検4級の問題として設定
                question_type='conversation_fill',
                question_text=question_text.strip(),
                explanation=explanation.strip(),
                question_number=question_num
            )

            # 選択肢を作成
            for i, choice_text in enumerate(choices, 1):
                is_correct = choice_text == correct_answer
                Choice.objects.create(
                    question=question,
                    choice_text=choice_text,
                    is_correct=is_correct,
                    order=i
                )

            self.stdout.write(f'Created question No.{question_num}')

        self.stdout.write(self.style.SUCCESS('Successfully created all conversation questions')) 