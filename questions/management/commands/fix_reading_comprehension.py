import re
from django.core.management.base import BaseCommand
from questions.models import ReadingPassage, ReadingQuestion, ReadingChoice

class Command(BaseCommand):
    help = 'Fix reading comprehension passages and questions with correct associations'

    def handle(self, *args, **options):
        # Clear existing data
        ReadingPassage.objects.all().delete()
        self.stdout.write('Cleared existing reading passages')
        
        # Read the text file
        with open('questions/reading_comprehesion_questions.txt', 'r', encoding='utf-8') as file:
            content = file.read()

        # Split into passages - only 3 dashes
        passages = re.split(r'-{3,}\n', content)
        
        for passage_block in passages:
            if not passage_block.strip():
                continue

            # Extract passage number and text
            passage_match = re.search(r'本文(\d+)\n(.*?)\n問題\1a:', passage_block, re.DOTALL)
            if not passage_match:
                continue
                
            passage_number = passage_match.group(1)
            passage_text = passage_match.group(2).strip()

            # Create passage
            passage = ReadingPassage.objects.create(
                text=passage_text,
                level='4',
                identifier=passage_number
            )
            
            self.stdout.write(f'Created passage {passage_number}')

            # Extract questions for this specific passage
            # Look for questions that start with the same passage number
            question_pattern = rf'問題{passage_number}([a-z]):\s*(.*?)\n選択肢{passage_number}\1:\s*(.*?)\n【正解{passage_number}\1】\s*(.*?)\n【解説{passage_number}\1】\s*(.*?)(?=\n\n|$|問題{passage_number}[a-z]:)'
            questions = re.finditer(question_pattern, passage_block, re.DOTALL)
            
            question_number = 1
            for question_match in questions:
                question_letter = question_match.group(1)
                question_text = question_match.group(2).strip()
                choices_text = question_match.group(3).strip()
                correct_answer = question_match.group(4).strip()
                explanation = question_match.group(5).strip()
                
                # Create question
                question = ReadingQuestion.objects.create(
                    passage=passage,
                    question_text=question_text,
                    question_number=question_number,
                    explanation=explanation
                )
                
                # Parse choices
                choice_lines = choices_text.split('\n')
                for i, choice_line in enumerate(choice_lines):
                    if choice_line.strip():
                        # Extract choice text (remove number and dot)
                        choice_text = re.sub(r'^\d+\.\s*', '', choice_line.strip())
                        is_correct = choice_text.strip() == correct_answer.strip()
                        
                        ReadingChoice.objects.create(
                            question=question,
                            choice_text=choice_text,
                            is_correct=is_correct,
                            order=i + 1
                        )
                
                self.stdout.write(f'  Created question {question_number} ({question_letter})')
                question_number += 1

        self.stdout.write(self.style.SUCCESS('Successfully fixed reading comprehension passages and questions')) 