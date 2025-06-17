from django.core.management.base import BaseCommand
from questions.models import ReadingPassage, ReadingQuestion, ReadingChoice

class Command(BaseCommand):
    help = 'Register reading comprehension questions from a text file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the text file containing questions')

    def handle(self, *args, **options):
        file_path = options['file_path']
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            # パッセージと設問を分離
            parts = content.split('\n\n')
            passage_text = parts[0].strip()
            
            # パッセージを登録
            passage = ReadingPassage.objects.create(text=passage_text)
            self.stdout.write(self.style.SUCCESS(f'Created passage with ID: {passage.id}'))
            
            # 設問を登録
            question_number = 1
            for part in parts[1:]:
                if not part.strip():
                    continue
                    
                lines = part.strip().split('\n')
                question_text = lines[0].strip()
                
                # 設問を登録
                question = ReadingQuestion.objects.create(
                    passage=passage,
                    question_text=question_text,
                    question_number=question_number
                )
                
                # 選択肢を登録
                for i, choice_text in enumerate(lines[1:], 1):
                    ReadingChoice.objects.create(
                        question=question,
                        choice_text=choice_text.strip(),
                        is_correct=(i == 1),  # 最初の選択肢を正解とする
                        order=i
                    )
                
                self.stdout.write(self.style.SUCCESS(f'Created question {question_number} with choices'))
                question_number += 1
                
            self.stdout.write(self.style.SUCCESS('Successfully registered reading comprehension questions'))
            
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}')) 