from django.core.management.base import BaseCommand
from exams.models import Question, Choice
import re

class Command(BaseCommand):
    help = 'Create listening illustration questions from text file'

    def handle(self, *args, **options):
        # 既存の問題を削除
        Question.objects.filter(question_type='listening_illustration').delete()
        self.stdout.write('Deleted existing listening illustration questions')

        # テキストファイルを読み込む
        with open('questions/listening_illustration_questions.txt', 'r', encoding='utf-8') as f:
            content = f.read()

        # 問題ごとに分割
        questions = re.split(r'\nNo\.', content)[1:]  # 最初の空文字列を除外

        for q_text in questions:
            # 問題番号を取得
            question_num = int(q_text.split('\n')[0])
            
            # 会話部分を抽出
            conversation_lines = []
            for line in q_text.split('\n'):
                if line.startswith('M:') or line.startswith('W:'):
                    conversation_lines.append(line)
            conversation = '\n'.join(conversation_lines)

            # 選択肢を抽出
            choices = []
            in_choices = False
            for line in q_text.split('\n'):
                if line.strip().startswith('Question No.'):
                    in_choices = True
                    continue
                if in_choices and line.strip() and not line.startswith('【'):
                    if line.strip().endswith('.'):
                        choices.append(line.strip())
                if line.startswith('【正解】'):
                    in_choices = False

            # 正解を抽出
            correct_answer = None
            for line in q_text.split('\n'):
                if line.startswith('【正解】'):
                    correct_answer = line.replace('【正解】', '').strip()
                    if correct_answer.startswith('1.') or correct_answer.startswith('2.') or correct_answer.startswith('3.'):
                        correct_answer = correct_answer[2:].strip()
                    break

            # 解説を抽出
            explanation = ''
            in_explanation = False
            for line in q_text.split('\n'):
                if line.startswith('【解説】'):
                    in_explanation = True
                    continue
                if in_explanation and line.strip():
                    explanation += line.strip() + '\n'
                if in_explanation and not line.strip():
                    break

        # 問題を作成
            question = Question.objects.create(
                level='4',  # 英検4級の問題として設定
                question_type='listening_illustration',
                question_text=conversation,
                explanation=explanation.strip(),
                audio_file=f'audio/part1/listening_illustration_question{question_num}.mp3',
                image_file=f'images/part1/2024_3_1ji_4_image_{question_num}.png',
                question_number=question_num  # 問題番号を設定
            )

            # 選択肢を作成
            for i, choice_text in enumerate(choices, 1):
                is_correct = choice_text == correct_answer
                Choice.objects.create(
                    question=question,
                    choice_text=choice_text,
                    is_correct=is_correct
                )

            self.stdout.write(f'Created question No.{question_num}')

        self.stdout.write(self.style.SUCCESS('Successfully created all listening illustration questions')) 