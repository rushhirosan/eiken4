from django.core.management.base import BaseCommand
from questions.models import ListeningQuestion, ListeningChoice
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'listening_illustration_questions.txt からイラスト問題を画像・音声付きで登録する（選択肢数も正確に）'

    def handle(self, *args, **options):
        # 既存のListeningQuestionを削除
        ListeningQuestion.objects.all().delete()
        self.stdout.write(self.style.WARNING('既存のListeningQuestionを全削除しました'))

        # ファイルパス
        base_dir = settings.BASE_DIR
        txt_path = os.path.join(base_dir, 'questions', 'listening_illustration_questions.txt')
        image_dir = os.path.join(base_dir, 'static', 'images', 'part1')
        audio_dir = os.path.join(base_dir, 'static', 'audio', 'part1')

        self.stdout.write(f'テキストファイルパス: {txt_path}')
        self.stdout.write(f'画像ディレクトリ: {image_dir}')
        self.stdout.write(f'音声ディレクトリ: {audio_dir}')

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

        self.stdout.write(f'問題ブロック数: {len(blocks)}')

        for block in blocks:
            lines = [l for l in block.split('\n') if l.strip()]
            if not lines:
                continue
            # 問題番号取得
            try:
                number = int(lines[0].replace('No.', '').replace(':', '').strip())
                self.stdout.write(f'処理中の問題番号: {number}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'問題番号の取得に失敗: {e}'))
                continue

            # 画像・音声ファイル名
            image_name = f'listening_illustration_image{number}.png'
            audio_name = f'listening_illustration_question{number}.mp3'
            image_path = os.path.join('images/part1', image_name)
            audio_path = os.path.join('audio/part1', audio_name)

            self.stdout.write(f'画像ファイル: {image_path}')
            self.stdout.write(f'音声ファイル: {audio_path}')

            # 選択肢の数を取得
            choices = []
            in_choices = False
            for line in lines[1:]:
                if line.strip().startswith('Question No.'):
                    in_choices = True
                    continue
                if in_choices and line.strip() and not line.startswith('【'):
                    if line.strip()[0].isdigit() and line.strip()[1] == '.':
                        choices.append(line.strip())
                if '【正解' in line:
                    break
            num_choices = len(choices)

            # モデル登録（問題文・正解は空でOK）
            q = ListeningQuestion.objects.create(
                question_text='',
                image=image_path,
                audio=audio_path,
                correct_answer='',
                level='4'
            )

            # 選択肢を番号のみで登録
            for i in range(1, num_choices + 1):
                ListeningChoice.objects.create(
                    question=q,
                    choice_text=str(i),
                    is_correct=False,  # 正解情報は使わない
                    order=i
                )

            self.stdout.write(self.style.SUCCESS(f'問題 No.{number} を登録（選択肢{num_choices}個）'))

        self.stdout.write(self.style.SUCCESS('全てのイラストリスニング問題を登録しました')) 