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

        for idx, q_text in enumerate(questions):
            if idx >= 10:
                break
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
            japanese_text = ''
            english_choices = ''
            english_text = ''
            
            expecting_correct_answer = False
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if expecting_correct_answer and correct_answer is None:
                    correct_answer = line
                    if correct_answer.startswith(('1.', '2.', '3.', '4.')):
                        correct_answer = correct_answer[2:].strip()
                    expecting_correct_answer = False
                    current_section = 'done'
                    continue
                if line.startswith('【正解】') or line.startswith('【正解'):
                    current_section = 'correct'
                    expecting_correct_answer = True
                    continue
                elif line.startswith('【解説】') or line.startswith('【解説'):
                    current_section = 'explanation'
                    continue
                elif line.startswith('選択肢'):
                    current_section = 'choices'
                    continue
                if current_section == 'question':
                    if re.match(r'^[①②③④⑤]', line):
                        english_choices += line + '\n'
                    elif re.match(r'^\(.*\)', line):
                        english_text += line + '\n'
                    else:
                        japanese_text += line + '\n'
                elif current_section == 'choices':
                    if re.match(r'^\d+\.', line):
                        choice_text = re.sub(r'^\d+\.\s*', '', line)
                        if choice_text not in choices:
                            choices.append(choice_text)
                elif current_section == 'explanation':
                    explanation += line + '\n'

            # 問題文を構造化して作成（「問題X:」の部分を削除）
            # 日本語文から「問題X:」の部分を削除
            japanese_text_clean = re.sub(r'^問題\d+:\s*', '', japanese_text.strip())
            question_text = f"{japanese_text_clean}\n{english_choices.strip()}\n{english_text.strip()}"

            # デバッグ用の出力
            self.stdout.write(f'Question {question_num} - Choices: {choices}')
            self.stdout.write(f'Question {question_num} - Correct: {correct_answer}')
            self.stdout.write(f'Question {question_num} - Explanation: {explanation.strip()}')

            # 問題を作成
            question = Question.objects.create(
                level='4',  # 英検4級の問題として設定
                question_type='word_order',
                question_text=question_text,
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