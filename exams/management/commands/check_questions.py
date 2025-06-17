from django.core.management.base import BaseCommand
from exams.models import Question, Choice

class Command(BaseCommand):
    help = 'Check registered questions'

    def handle(self, *args, **options):
        questions = Question.objects.filter(question_type='listening_illustration')
        
        for question in questions:
            self.stdout.write(self.style.SUCCESS(f'\nQuestion: {question.question_text}'))
            self.stdout.write(f'Listening Text:\n{question.listening_text}')
            self.stdout.write('\nChoices:')
            for choice in question.choices.all():
                self.stdout.write(f'{choice.choice_text} (Correct: {choice.is_correct})')
            self.stdout.write(f'\nExplanation:\n{question.explanation}')
            self.stdout.write('-' * 50) 