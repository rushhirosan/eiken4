from django.core.management.base import BaseCommand
from exams.models import Question, Choice
import re

class Command(BaseCommand):
    help = 'listening_passage_questions.txt から問題31-40の文章問題を登録する'

    def handle(self, *args, **options):
        # 既存の問題を削除（31-40のみ）
        Question.objects.filter(
            question_type='listening_passage',
            question_number__in=range(31, 41)
        ).delete()
        self.stdout.write(self.style.WARNING('既存のリスニング文章問題（31-40）を削除しました'))
        
        # ファイルから問題を読み取る
        file_path = 'questions/listening_passage_questions.txt'
        questions_data = self.extract_questions_from_file(file_path)
        
        self.stdout.write(f'抽出された問題数: {len(questions_data)}')
        
        # 問題を作成
        for q_data in questions_data:
            # 問題を作成
            question = Question.objects.create(
                question_type='listening_passage',
                level='4',
                question_number=q_data['question_number'],
                question_text=q_data['passage'] + '\n' + q_data['question_text'],
                explanation=q_data['explanation'],
                audio_file=f'audio/part3/listening_passage_question{q_data["question_number"]}.mp3'
            )
            
            # 選択肢を作成
            for i, choice_text in enumerate(q_data['choices']):
                Choice.objects.create(
                    question=question,
                    choice_text=choice_text,
                    is_correct=(i == q_data['correct_choice_index']),
                    order=i + 1
                )
            
            self.stdout.write(self.style.SUCCESS(f'問題{q_data["question_number"]}を登録'))
        
        self.stdout.write(self.style.SUCCESS('問題31-40のリスニング文章問題を登録しました'))

    def extract_questions_from_file(self, file_path):
        questions_data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 問題ブロックを分割
            question_blocks = content.split('---')
            for block in question_blocks:
                if not block.strip():
                    continue
                # 問題番号を抽出
                number_match = re.search(r'No\.(\d+):', block)
                if not number_match:
                    continue
                question_number = int(number_match.group(1))
                
                # 31-40のみを処理
                if question_number < 31 or question_number > 40:
                    continue
                
                # パッセージ文を抽出（No.X: から Question No.X: の直前まで）
                passage_match = re.search(r'No\.\d+:\s*(.*?)\n\s*Question No\.', block, re.DOTALL)
                passage = passage_match.group(1).strip() if passage_match else ''
                
                # 問題文を抽出
                question_text_match = re.search(r'Question No\.\d+:\s*(.*?)\n\s*1\.', block, re.DOTALL)
                question_text = question_text_match.group(1).strip() if question_text_match else ''
                
                # 選択肢を抽出
                choices = []
                for i in range(1, 5):
                    choice_match = re.search(rf'{i}\.\s*(.*?)(?=\n\d\.\s|\n【正解|\n$)', block, re.DOTALL)
                    if choice_match:
                        choices.append(choice_match.group(1).strip())
                
                # 正解を抽出
                correct_match = re.search(r'【正解\d+】\s*(\d+)\.', block)
                correct_choice_index = int(correct_match.group(1)) - 1 if correct_match else 0
                
                # 解説を抽出
                explanation_match = re.search(r'【解説\d+】\s*(.+)', block, re.DOTALL)
                explanation = explanation_match.group(1).strip() if explanation_match else ''
                
                # データ追加
                if question_text and choices:
                    questions_data.append({
                        'question_number': question_number,
                        'passage': passage,
                        'question_text': question_text,
                        'choices': choices,
                        'correct_choice_index': correct_choice_index,
                        'explanation': explanation
                    })
        return questions_data 