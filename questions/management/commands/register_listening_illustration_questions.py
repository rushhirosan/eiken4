from django.core.management.base import BaseCommand
from questions.models import ListeningQuestion, ListeningChoice
import os
from django.conf import settings
import random

class Command(BaseCommand):
    help = 'listening_illustration_questions.txt からイラスト問題を画像・音声付きで登録する'

    def handle(self, *args, **options):
        # 既存のListeningQuestionを削除
        ListeningQuestion.objects.all().delete()
        self.stdout.write(self.style.WARNING('既存のListeningQuestionを全削除しました'))

        # ファイルパス
        base_dir = settings.BASE_DIR
        txt_path = os.path.join(base_dir, 'questions', 'listening_illustration_questions.txt')
        image_dir = os.path.join(base_dir, 'static', 'images', 'part1')
        audio_dir = os.path.join(base_dir, 'static', 'audio', 'part1')

        if not os.path.exists(txt_path):
            self.stdout.write(self.style.ERROR(f'ファイルが見つかりません: {txt_path}'))
            return

        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 問題ごとに分割
        blocks = []
        current_block = []
        for line in content.split('\n'):
            if line.strip().startswith('No.'):
                if current_block:
                    blocks.append('\n'.join(current_block))
                current_block = [line]
            else:
                current_block.append(line)
        if current_block:
            blocks.append('\n'.join(current_block))

        for block in blocks:
            lines = [l for l in block.split('\n') if l.strip()]
            if not lines:
                continue
            # 問題番号取得
            try:
                number = int(lines[0].replace('No.', '').strip())
            except Exception:
                continue
            # 画像・音声ファイル名
            image_name = f'2024_3_1ji_4_image_{number}.png'
            audio_name = f'2024_3_1ji_4_audio_{number}.mp3'
            image_path = os.path.join('images/part1', image_name)
            audio_path = os.path.join('audio/part1', audio_name)

            # 問題文・選択肢・正解
            question_text = ''
            choices = []
            correct_answer = ''
            in_choices = False
            for line in lines[1:]:
                if line.strip().startswith('M:') or line.strip().startswith('W:'):
                    question_text += line.strip() + '\n'
                if line.strip().startswith('Question No.'):
                    in_choices = True
                    continue
                if in_choices and line.strip() and not line.startswith('【'):
                    if line.strip().endswith('.'):
                        choices.append(line.strip())
                if line.startswith('【正解'):
                    # 例: 【正解1】\n1. Around ten.
                    idx = lines.index(line)
                    if idx + 1 < len(lines):
                        correct_answer = lines[idx + 1].strip()
            if not question_text or not choices or not correct_answer:
                self.stdout.write(self.style.ERROR(f'問題データ不備: No.{number}'))
                continue

            # モデル登録
            q = ListeningQuestion.objects.create(
                question_text=question_text.strip(),
                image=image_path,
                audio=audio_path,
                correct_answer=correct_answer,
                level='4'
            )

            # 選択肢を登録
            for i, choice_text in enumerate(choices, 1):
                ListeningChoice.objects.create(
                    question=q,
                    choice_text=choice_text,
                    is_correct=(choice_text == correct_answer),
                    order=i
                )

            self.stdout.write(self.style.SUCCESS(f'問題 No.{number} を登録しました'))

        self.stdout.write(self.style.SUCCESS('全てのイラストリスニング問題を登録しました')) 