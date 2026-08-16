from django.core.management.base import BaseCommand
from exams.models import Question
from questions.models import ListeningQuestion
from questions.level_paths import (
    db_audio_path,
    db_image_path_part1,
    listening_illustration_audio_part,
)
import re


class Command(BaseCommand):
    help = 'Update audio/image file paths for listening questions (level-aware)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--level',
            type=str,
            default='4',
            choices=['3', '4', '5'],
            help='対象級（既定: 4）',
        )

    def handle(self, *args, **options):
        level = options['level']

        conversation_questions = Question.objects.filter(
            question_type='listening_conversation',
            level=level,
        ).order_by('question_number', 'id')

        for idx, question in enumerate(conversation_questions, start=1):
            n = question.question_number if question.question_number >= 1 else idx
            question.audio_file = db_audio_path(
                level, 'part2', f'listening_conversation_question{n}.mp3'
            )
            question.save()
            self.stdout.write(
                self.style.SUCCESS(f'Updated audio path (No.{n}): {question.audio_file}')
            )

        passage_questions = Question.objects.filter(
            question_type='listening_passage',
            level=level,
        ).order_by('question_number', 'id')

        for idx, question in enumerate(passage_questions, start=1):
            n = question.question_number if question.question_number >= 1 else idx
            question.audio_file = db_audio_path(
                level, 'part3', f'listening_passage_question{n}.mp3'
            )
            question.save()
            self.stdout.write(
                self.style.SUCCESS(f'Updated audio path (No.{n}): {question.audio_file}')
            )

        illustration_questions = ListeningQuestion.objects.filter(
            level=level
        ).order_by('id')

        for idx, question in enumerate(illustration_questions, start=1):
            n = idx
            # 既存パスに番号があればそれを優先
            m = re.search(r'listening_illustration_question(\d+)', question.audio or '')
            if m:
                n = int(m.group(1))
            part = listening_illustration_audio_part(level, n)
            question.audio = db_audio_path(
                level, part, f'listening_illustration_question{n}.mp3'
            )
            question.image = db_image_path_part1(
                level, f'listening_illustration_image{n}.png'
            )
            question.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Updated paths for No.{n}: {question.audio}, {question.image}'
                )
            )
