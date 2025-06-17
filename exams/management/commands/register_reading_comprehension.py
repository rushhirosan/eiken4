import re
from django.core.management.base import BaseCommand
from questions.models import ReadingPassage, ReadingQuestion, ReadingChoice

class Command(BaseCommand):
    help = 'Register reading comprehension questions from text file'

    def handle(self, *args, **options):
        # 既存のデータを削除
        ReadingQuestion.objects.all().delete()
        ReadingPassage.objects.all().delete()
        self.stdout.write('Deleted all existing reading_passage and reading_comprehension questions.')

        # テキストファイルを読み込む
        with open('questions/reading_comprehesion_questions.txt', 'r', encoding='utf-8') as file:
            content = file.read()

        # 本文を抽出
        passage_pattern = r'(本文[a-z]\n.*?)(?=---|\Z)'
        passages = re.finditer(passage_pattern, content, re.DOTALL)

        for passage_match in passages:
            passage_block = passage_match.group(1)
            passage_id = re.search(r'本文([a-z])', passage_block).group(1)
            
            # 本文テキスト（最初の空行まで or 問題の直前まで）
            passage_text_match = re.search(r'本文[a-z]\n([\s\S]*?)(?=問題[a-z]\d+:)', passage_block)
            passage_text = passage_text_match.group(1).strip() if passage_text_match else passage_block.strip()

            # 本文を作成
            passage = ReadingPassage.objects.create(
                text=passage_text
            )
            self.stdout.write(f'Created passage {passage_id}')

            # 問題ブロックを抽出（このパッセージ内のみ）
            question_pattern = r'問題(' + passage_id + r'\d+):\n(.*?)(?=選択肢' + passage_id + r'\d+:|問題' + passage_id + r'\d+:|$)'
            questions = re.finditer(question_pattern, passage_block, re.DOTALL)

            for question_match in questions:
                question_id = question_match.group(1)
                question_text = question_match.group(2).strip()

                # 選択肢を抽出
                choice_pattern = r'選択肢' + question_id + r'(?::|\n)(.*?)(?=【正解' + question_id + r'】|(?:選択肢|問題)' + passage_id + r'\d+:|$)'
                choice_match = re.search(choice_pattern, passage_block, re.DOTALL)
                
                if choice_match:
                    choices_text = choice_match.group(1).strip()
                    choices = [c.strip() for c in choices_text.split('\n') if c.strip()]

                    # 正解を抽出
                    correct_pattern = r'【正解' + question_id + r'】\n(.*?)(?=【解説|$)'
                    correct_match = re.search(correct_pattern, passage_block, re.DOTALL)
                    correct_answer = correct_match.group(1).strip() if correct_match else ''

                    # 問題を作成
                    question = ReadingQuestion.objects.create(
                        passage=passage,
                        question_text=question_text,
                        question_number=int(question_id[1:])
                    )

                    # 選択肢を作成
                    for i, choice_text in enumerate(choices, 1):
                        is_correct = choice_text == correct_answer
                        ReadingChoice.objects.create(
                            question=question,
                            choice_text=choice_text,
                            is_correct=is_correct,
                            order=i
                        )

                    self.stdout.write(f'Created question {question_id} with choices') 