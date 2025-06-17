from django.core.management.base import BaseCommand
from exams.models import Question, Choice
import re

class Command(BaseCommand):
    help = 'Create reading comprehension questions from text file'

    def handle(self, *args, **options):
            # 既存の長文読解問題を削除
            Question.objects.filter(question_type__in=['reading_comprehension', 'reading_passage']).delete()
        self.stdout.write('Deleted existing reading comprehension and passage questions')

        # テキストファイルを読み込む
        with open('questions/reading_comprehesion_questions.txt', 'r', encoding='utf-8') as f:
            content = f.read()

        # 問題ごとに分割
        passages = re.split(r'\n---\n', content)

        for passage_text in passages:
            if not passage_text.strip():
                continue

            # 本文の識別子（a, b, c）を取得
            passage_id_match = re.search(r'問題([a-z])\n', passage_text)
            if not passage_id_match:
                continue
            passage_id = passage_id_match.group(1)

            # 本文部分を抽出（最初の選択肢や設問が出てくるまで）
            lines = passage_text.split('\n')
            passage_lines = []
            i = 1  # 0は"問題a"などなのでスキップ
            while i < len(lines):
                line = lines[i].strip()
                if line.startswith('選択肢'):
                    break
                passage_lines.append(line)
                i += 1
            passage_body = '\n'.join(passage_lines).strip()

            # 本文をQuestionとして登録
            passage_question = Question.objects.create(
                level='4',
                question_type='reading_passage',
                question_text=passage_body,
                identifier=passage_id,
                question_number=1
            )
            self.stdout.write(f'Created passage {passage_id}')

            # 設問ごとに分割
            question_blocks = re.finditer(r'選択肢([a-z]\d*):\n(.*?)(?=選択肢[a-z]\d*:|$)', passage_text, re.DOTALL)
            
            for match in question_blocks:
                sub_id = match.group(1)
                question_block = match.group(2).strip()
                
                # 設問文、選択肢、正解、解説を抽出
                lines = question_block.split('\n')
                q_text = ''
                choices = []
                correct_answer = None
                explanation = ''
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
                    elif re.match(r'^\d+\.', line):
                        current_section = 'choices'
                        
                    if current_section == 'question':
                        q_text += line + '\n'
                    elif current_section == 'choices':
                        if re.match(r'^\d+\.', line):
                            choice_text = re.sub(r'^\d+\.\s*', '', line)
                            choices.append(choice_text)
                    elif current_section == 'correct':
                        correct_answer = line
                        if correct_answer.startswith(('1.', '2.', '3.', '4.')):
                            correct_answer = correct_answer[2:].strip()
                    elif current_section == 'explanation':
                        explanation += line + '\n'

                # 設問をQuestionとして登録
                q_obj = Question.objects.create(
                    level='4',
                    question_type='reading_comprehension',
                    question_text=q_text.strip(),
                    explanation=explanation.strip(),
                    passage=passage_question,
                    identifier=sub_id,
                    question_number=int(re.search(r'\d+', sub_id).group())
                )

                # 選択肢を登録
                for i, choice_text in enumerate(choices, 1):
                    is_correct = choice_text == correct_answer
                    Choice.objects.create(
                        question=q_obj,
                        choice_text=choice_text,
                        is_correct=is_correct,
                        order=i
                    )
                self.stdout.write(f'Created sub-question {sub_id} for passage {passage_id} with {len(choices)} choices')

        self.stdout.write(self.style.SUCCESS('Successfully created all reading comprehension questions')) 