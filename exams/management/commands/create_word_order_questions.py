from django.core.management.base import BaseCommand
from exams.models import Question, Choice
import re

class Command(BaseCommand):
    help = 'Create word order questions from text file'

    def handle(self, *args, **options):
        # 既存の問題を削除
        Question.objects.filter(question_type='word_order').delete()
        self.stdout.write('Deleted existing word order questions')

        # テキストファイルを読み込む
        with open('questions/wordorder_questions.txt', 'r', encoding='utf-8') as f:
            content = f.read()

        # 問題ごとに分割
        questions = re.split(r'\n---\n', content)

        for q_text in questions:
            if not q_text.strip():
                continue

            # 問題番号を取得
            question_match = re.search(r'問題(\d+)', q_text)
            if not question_match:
                continue
            question_num = int(question_match.group(1))
            
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
                    
                if line.startswith('【正解】'):
                    current_section = 'correct'
                    continue
                elif line.startswith('【解説】'):
                    current_section = 'explanation'
                    continue
                elif line.startswith('選択肢'):
                    current_section = 'choices'
                    continue
                
                if current_section == 'question':
                    # 選択肢の行（①②③④⑤で始まる行）も問題文に含める
                    question_text += line + '\n'
                elif current_section == 'choices':
                    # 選択肢の行を処理
                    if re.match(r'^\d+\.', line):
                        # 行の先頭の数字とドットを除去
                        choice_text = re.sub(r'^\d+\.\s*', '', line)
                        # 選択肢の番号（①②③④⑤）を除去
                        choice_text = re.sub(r'^[①②③④⑤]\s*─\s*', '', choice_text)
                        choices.append(choice_text)
                elif current_section == 'correct':
                    correct_answer = line
                    if correct_answer.startswith(('1.', '2.', '3.', '4.')):
                        correct_answer = correct_answer[2:].strip()
                elif current_section == 'explanation':
                    explanation += line + '\n'

            # 問題を作成
            question = Question.objects.create(
                level='4',  # 英検4級の問題として設定
                question_type='word_order',
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

        self.stdout.write(self.style.SUCCESS('Successfully created all word order questions')) 