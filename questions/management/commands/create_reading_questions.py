import re
from django.core.management.base import BaseCommand
from questions.models import Question, Choice, Passage

class Command(BaseCommand):
    help = 'Register reading comprehension questions from a text file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the text file containing questions')

    def handle(self, *args, **options):
        file_path = options['file_path']
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            # Split content into main sections (each passage with its questions)
            sections = re.split(r'---\n', content)
            
            for section in sections:
                if not section.strip():
                    continue
                    
                # Extract passage
                passage_match = re.search(r'問題[a-z]\n(.*?)(?=選択肢)', section, re.DOTALL)
                if not passage_match:
                    continue
                    
                passage_text = passage_match.group(1).strip()
                
                # Create passage
                passage = Passage.objects.create(
                    text=passage_text,
                    category='reading_comprehension'
                )
                
                # Extract questions and choices
                question_blocks = re.finditer(
                    r'(?:選択肢|問題)([a-z]\d+):\n(.*?)(?=【正解\1】|(?:選択肢|問題)[a-z]\d+:|$)', 
                    section, 
                    re.DOTALL
                )
                
                for q_block in question_blocks:
                    question_text = q_block.group(2).strip()
                    
                    # Create question
                    question = Question.objects.create(
                        text=question_text,
                        category='reading_comprehension',
                        passage=passage
                    )
                    
                    # Extract choices
                    choices_text = re.search(
                        r'【正解\1】\n(.*?)(?=【解説\1】|$)', 
                        section[q_block.end():], 
                        re.DOTALL
                    )
                    
                    if choices_text:
                        choices = choices_text.group(1).strip().split('\n')
                        for choice in choices:
                            if choice.strip():
                                Choice.objects.create(
                                    question=question,
                                    text=choice.strip(),
                                    is_correct=choice.strip().startswith('正解')
                                )
                
            self.stdout.write(self.style.SUCCESS('Successfully registered reading comprehension questions'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}')) 