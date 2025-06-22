from django.core.management.base import BaseCommand
from questions.models import ReadingPassage, ReadingQuestion, ReadingChoice
import re

class Command(BaseCommand):
    help = 'Register reading comprehension passages and questions from text file'

    def handle(self, *args, **options):
        # Clear existing data
        ReadingPassage.objects.all().delete()
        
        # Read the text file
        with open('questions/reading_comprehesion_questions.txt', 'r', encoding='utf-8') as file:
            content = file.read()

        # Split into passages
        passages = content.split('---')
        
        for passage_block in passages:
            if not passage_block.strip():
                continue

            # Extract passage text
            passage_match = re.search(r'本文\d+\n(.*?)\n問題\d+a:', passage_block, re.DOTALL)
            if not passage_match:
                continue
            passage_text = passage_match.group(1).strip()

            # Create passage
            passage = ReadingPassage.objects.create(
                text=passage_text,
                level='4'  # Default to Grade 4
            )

            # Extract all questions for this passage
            questions = re.finditer(r'問題\d+[a-z]:\s*(.*?)\n選択肢\d+[a-z]:\s*(.*?)\n【正解\d+[a-z]】\s*(.*?)\n【解説\d+[a-z]】\s*(.*?)(?=\n\n|$)', passage_block, re.DOTALL)
            
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

            self.stdout.write(self.style.SUCCESS(f'Successfully registered passage with {i} questions')) 