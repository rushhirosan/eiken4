import os
import re
from django.core.management.base import BaseCommand
from questions.models import ReadingPassage, ReadingQuestion, ReadingChoice
from django.conf import settings

class Command(BaseCommand):
    help = 'Register passages for 問題a and 問題b, and their respective questions (a1, a2 for 問題a; b1, b2, b3 for 問題b).'

    def handle(self, *args, **options):
        # 既存のデータを削除
        ReadingPassage.objects.all().delete()
        
        file_path = os.path.join(settings.BASE_DIR, 'questions', 'reading_comprehesion_questions.txt')
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return

        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # 問題aと問題bのブロックを抽出
        passage_blocks = re.split(r'-{3,}\n', content)
        for block in passage_blocks:
            if not block.strip():
                continue
            # パッセージタイトル（問題a または 問題b）と本文
            m = re.search(r'問題([abc])\n(.+?)(?=\n選択肢[a-z]\d|\Z)', block, re.DOTALL)
            if not m:
                continue
            passage_label = m.group(1)
            passage_text = m.group(2).strip()
            passage = ReadingPassage.objects.create(
                text=passage_text,
                level='4',
                identifier=passage_label
            )
            self.stdout.write(self.style.SUCCESS(f'Created passage {passage_label}'))

            # 設問を抽出
            if passage_label == 'a':
                question_numbers = ['a1', 'a2']
            elif passage_label == 'b':
                question_numbers = ['b1', 'b2', 'b3']
            elif passage_label == 'c':
                question_numbers = ['c1', 'c2', 'c3', 'c4', 'c5']
            else:
                continue

            for qnum in question_numbers:
                m_q = re.search(rf'選択肢{qnum}[:：]?\n([\s\S]+?)(?=\n選択肢[a-z]\d|\Z)', block)
                if not m_q:
                    continue
                qblock = m_q.group(1)
                # 問題文（最初の空行まで）
                q_lines = qblock.split('\n')
                question_text = ''
                choices_lines = []
                found_choices = False
                for line in q_lines:
                    if re.match(r'\d+\. ', line.strip()):
                        found_choices = True
                    if found_choices:
                        choices_lines.append(line)
                    else:
                        question_text += line + '\n'
                question_text = question_text.strip()
                # ReadingQuestion作成
                question = ReadingQuestion.objects.create(
                    passage=passage,
                    question_text=question_text,
                    question_number=int(re.search(r'\d+', qnum).group())
                )
                # 選択肢を抽出
                choices = []
                for line in choices_lines:
                    m_c = re.match(r'(\d+)\.\s*(.+)', line.strip())
                    if m_c:
                        choices.append(m_c.group(2))
                # 正解を抽出
                correct = None
                correct_m = re.search(rf'【正解{qnum}】\n(.+)', block)
                if correct_m:
                    correct = correct_m.group(1).strip().split('\n')[0]
                # ReadingChoice作成
                for idx, choice in enumerate(choices, 1):
                    is_correct = (choice.strip() == correct)
                    ReadingChoice.objects.create(
                        question=question,
                        choice_text=choice.strip(),
                        is_correct=is_correct,
                        order=idx
                    )
                self.stdout.write(self.style.SUCCESS(f'Created question {qnum} with choices'))
        self.stdout.write(self.style.SUCCESS('Registered all passages and questions')) 