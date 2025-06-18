from django.core.management.base import BaseCommand
from questions.models import ListeningQuestion, ListeningChoice

class Command(BaseCommand):
    help = 'リスニングイラスト問題のデータを更新して、問題文と選択肢テキストを空にする'

    def handle(self, *args, **options):
        # リスニングイラスト問題を取得
        questions = ListeningQuestion.objects.filter(level='4')
        
        for question in questions:
            # 問題文を空にする
            question.question_text = ''
            # 正解のテキストも空にする
            question.correct_answer = ''
            question.save()
            
            # 選択肢のテキストを空にする（番号のみ残す）
            choices = ListeningChoice.objects.filter(question=question).order_by('order')
            for i, choice in enumerate(choices, 1):
                choice.choice_text = str(i)
                choice.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'問題 {question.id} を更新しました')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'合計 {questions.count()} 問を更新しました')
        ) 