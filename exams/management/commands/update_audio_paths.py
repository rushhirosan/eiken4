from django.core.management.base import BaseCommand
from exams.models import Question
from questions.models import ListeningQuestion

class Command(BaseCommand):
    help = 'Update audio file paths for listening questions'

    def handle(self, *args, **options):
        # リスニング会話問題の音声ファイルパスを更新
        conversation_questions = Question.objects.filter(
            question_type='listening_conversation',
            level='4'
        ).order_by('id')

        for i, question in enumerate(conversation_questions, 1):
            question.audio_file = f'audio/part2/listening_conversation_question{i}.mp3'
            question.save()
            self.stdout.write(
                self.style.SUCCESS(f'Updated audio path for question {i}: {question.audio_file}')
            )

        # リスニング文章問題の音声ファイルパスを更新
        passage_questions = Question.objects.filter(
            question_type='listening_passage',
            level='4'
        ).order_by('id')

        for i, question in enumerate(passage_questions, 1):
            question.audio_file = f'audio/part3/listening_passage_question{i}.mp3'
            question.save()
            self.stdout.write(
                self.style.SUCCESS(f'Updated audio path for question {i}: {question.audio_file}')
            )

        # リスニングイラスト問題の音声ファイルパスを更新（ListeningQuestionモデルを使用）
        illustration_questions = ListeningQuestion.objects.filter(
            level='4'
        ).order_by('id')

        for i, question in enumerate(illustration_questions, 1):
            question.audio = f'audio/part1/listening_illustration_question{i}.mp3'
            question.image = f'images/part1/listening_illustration_image{i}.png'
            question.save()
            self.stdout.write(
                self.style.SUCCESS(f'Updated audio and image paths for question {i}: {question.audio}, {question.image}')
            ) 