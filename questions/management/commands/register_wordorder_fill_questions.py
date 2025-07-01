from django.core.management.base import BaseCommand
from exams.models import Question, Choice
import re

class Command(BaseCommand):
    help = 'Register word order fill questions from text file'

    def handle(self, *args, **options):
        # Clear existing questions
        Question.objects.filter(question_type='word_order').delete()
        self.stdout.write(self.style.WARNING('Cleared existing word order questions'))
        
        # Read the text file
        with open('questions/wordorder_questions.txt', 'r', encoding='utf-8') as file:
            content = file.read()

        # Split into questions
        questions = content.split('---')
        
        registered_count = 0
        for i, question_block in enumerate(questions, 1):
            if not question_block.strip():
                continue

            try:
                # Extract question text (日本語文＋英語文)
                question_match = re.search(r'問題\d+:\s*(.*?)\n選択肢\d+:', question_block, re.DOTALL)
                if not question_match:
                    self.stdout.write(self.style.WARNING(f'Could not extract question text from question {i}'))
                    continue
                question_text = question_match.group(1).strip()

                # Extract choices
                choices_match = re.search(r'選択肢\d+:\s*(.*?)\n【正解\d+】', question_block, re.DOTALL)
                if not choices_match:
                    self.stdout.write(self.style.WARNING(f'Could not extract choices from question {i}'))
                    continue
                choices_text = choices_match.group(1).strip()
                choices = [c.strip() for c in choices_text.split('\n') if c.strip() and c.strip().startswith(('1.', '2.', '3.', '4.'))]

                # Extract correct answer
                correct_match = re.search(r'【正解\d+】\s*(.*?)\n【解説\d+】', question_block, re.DOTALL)
                if not correct_match:
                    self.stdout.write(self.style.WARNING(f'Could not extract correct answer from question {i}'))
                    continue
                correct_answer = correct_match.group(1).strip()

                # Extract explanation
                explanation_match = re.search(r'【解説\d+】\s*(.*?)(?=\n\n|$)', question_block, re.DOTALL)
                explanation = explanation_match.group(1).strip() if explanation_match else ''

                # Create question
                question = Question.objects.create(
                    question_text=question_text,
                    level='4',  # Default to Grade 4
                    question_type='word_order',
                    explanation=explanation
                )

                # Create choices
                for order, choice_text in enumerate(choices, 1):
                    # Remove the number prefix (1., 2., etc.) for comparison
                    clean_choice = re.sub(r'^\d+\.\s*', '', choice_text.strip())
                    clean_correct = re.sub(r'^\d+\.\s*', '', correct_answer.strip())
                    is_correct = clean_choice == clean_correct
                    
                    Choice.objects.create(
                        question=question,
                        choice_text=clean_choice,
                        is_correct=is_correct,
                        order=order
                    )

                registered_count += 1
                self.stdout.write(self.style.SUCCESS(f'Successfully registered question {i}'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing question {i}: {str(e)}'))
                continue

        self.stdout.write(self.style.SUCCESS(f'Registration completed! {registered_count} questions registered.')) 