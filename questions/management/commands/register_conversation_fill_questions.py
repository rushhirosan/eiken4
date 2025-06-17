from django.core.management.base import BaseCommand
from exams.models import Question, Choice
import re

class Command(BaseCommand):
    help = 'Register conversation fill questions from text file'

    def handle(self, *args, **options):
        # Clear existing questions
        Question.objects.filter(question_type='conversation_fill').delete()
        
        # Read the text file
        with open('questions/conversation_questions.txt', 'r', encoding='utf-8') as file:
            content = file.read()

        # Split into questions
        questions = content.split('---')
        
        for i, question_block in enumerate(questions[:10], 1):  # Only process first 10 questions
            if not question_block.strip():
                continue

            # Extract question text
            question_match = re.search(r'問題\d+:\s*(.*?)\s*選択肢\d+:', question_block, re.DOTALL)
            if not question_match:
                continue
            question_text = question_match.group(1).strip()

            # Extract choices
            choices_match = re.search(r'選択肢\d+:\s*(.*?)\s*【正解\d+】', question_block, re.DOTALL)
            if not choices_match:
                continue
            choices_text = choices_match.group(1).strip()
            choices = [c.strip() for c in choices_text.split('\n') if c.strip()]

            # Extract correct answer
            correct_match = re.search(r'【正解\d+】\s*(.*?)\s*【解説\d+】', question_block, re.DOTALL)
            if not correct_match:
                continue
            correct_answer = correct_match.group(1).strip()

            # Extract explanation
            explanation_match = re.search(r'【解説\d+】\s*(.*?)(?=\n\n|$)', question_block, re.DOTALL)
            explanation = explanation_match.group(1).strip() if explanation_match else ''

            # Create question
            question = Question.objects.create(
                question_text=question_text,
                level='4',  # Default to Grade 4
                question_type='conversation_fill',
                explanation=explanation
            )

            # Create choices
            for order, choice_text in enumerate(choices, 1):
                is_correct = choice_text == correct_answer
                Choice.objects.create(
                    question=question,
                    choice_text=choice_text,
                    is_correct=is_correct,
                    order=order
                )

            self.stdout.write(self.style.SUCCESS(f'Successfully registered question {i}')) 