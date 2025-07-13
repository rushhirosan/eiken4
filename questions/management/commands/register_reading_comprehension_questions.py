from django.core.management.base import BaseCommand
from questions.models import ReadingPassage, ReadingQuestion, ReadingChoice
import re

class Command(BaseCommand):
    help = 'Register reading comprehension passages 10-12 and questions from text file'

    def handle(self, *args, **options):
        # Clear existing passages 10-12
        ReadingPassage.objects.filter(identifier__in=['10', '11', '12']).delete()
        self.stdout.write(self.style.WARNING('既存の読解問題（本文10-12）を削除しました'))
        
        # Read the text file
        with open('questions/reading_comprehesion_questions.txt', 'r', encoding='utf-8') as file:
            content = file.read()

        # Split into passages
        passages = content.split('---')
        
        for passage_block in passages:
            if not passage_block.strip():
                continue

            # Extract passage number
            passage_number_match = re.search(r'本文(\d+)', passage_block)
            if not passage_number_match:
                continue
            passage_number = int(passage_number_match.group(1))
            
            # Only process passages 10-12
            if passage_number < 10 or passage_number > 12:
                continue

            # Extract passage text (everything from 本文 to the first question)
            passage_match = re.search(r'本文\d+\s*\n(.*?)(?=\n問題\d+[a-z]:)', passage_block, re.DOTALL)
            if not passage_match:
                continue
            passage_text = passage_match.group(1).strip()

            # Create passage
            passage = ReadingPassage.objects.create(
                text=passage_text,
                level='4',  # Default to Grade 4
                identifier=str(passage_number)
            )

            # Extract all questions for this passage
            questions = re.finditer(r'問題\d+[a-z]:\s*(.*?)\n選択肢\d+[a-z]:\s*(.*?)\n【正解\d+[a-z]】\s*(.*?)\n【解説\d+[a-z]】\s*(.*?)(?=\n問題\d+[a-z]:|\n---|$)', passage_block, re.DOTALL)
            
            question_count = 0
            for i, question_match in enumerate(questions, 1):
                question_text = question_match.group(1).strip()
                choices_text = question_match.group(2).strip()
                correct_answer = question_match.group(3).strip()
                explanation = question_match.group(4).strip()

                # 正解の番号を除去（例：「3. Go fishing」→「Go fishing」）
                if correct_answer.startswith(('1.', '2.', '3.', '4.')):
                    correct_answer = correct_answer[2:].strip()

                # Create question
                question = ReadingQuestion.objects.create(
                    passage=passage,
                    question_text=question_text,
                    question_number=i,
                    explanation=explanation
                )

                # Create choices
                choices = [c.strip() for c in choices_text.split('\n') if c.strip()]
                for order, choice_text in enumerate(choices, 1):
                    # 選択肢の番号を除去（例：「3. Go fishing」→「Go fishing」）
                    if choice_text.startswith(('1.', '2.', '3.', '4.')):
                        choice_text = choice_text[2:].strip()
                    is_correct = choice_text == correct_answer
                    
                    ReadingChoice.objects.create(
                        question=question,
                        choice_text=choice_text,
                        is_correct=is_correct,
                        order=order
                    )
                question_count += 1

            self.stdout.write(self.style.SUCCESS(f'本文{passage_number}と{question_count}問の問題を登録しました'))
        
        self.stdout.write(self.style.SUCCESS('登録完了'))
        
        # 確認
        total_passages = ReadingPassage.objects.count()
        total_questions = ReadingQuestion.objects.count()
        self.stdout.write(self.style.SUCCESS(f'データベース内の読解問題総数: 本文{total_passages}個、問題{total_questions}問')) 