import os

from django.core.management.base import BaseCommand
from questions.models import ListeningQuestion, ListeningChoice

from questions.level_paths import (
    add_default_register_arguments,
    db_audio_path,
    db_image_path_part1,
    listening_illustration_audio_part,
    questions_file_abspath,
    static_audio_dir,
    static_images_part1_dir,
)


class Command(BaseCommand):
    help = 'listening_illustration_questions.txt からイラスト問題を画像・音声付きで登録する（問題数上限なし）'

    def add_arguments(self, parser):
        add_default_register_arguments(parser)

    def handle(self, *args, **options):
        level = options['level']
        if level == '4':
            for i in range(1, 41):
                ListeningQuestion.objects.filter(level='4').filter(
                    image__endswith=f'listening_illustration_image{i}.png'
                ).delete()
        else:
            ListeningQuestion.objects.filter(level=level).delete()
        self.stdout.write(self.style.WARNING(f'既存のListeningQuestion（level={level}）を削除しました'))

        txt_path = questions_file_abspath(level, 'listening_illustration_questions.txt')
        image_dir = static_images_part1_dir(level)

        self.stdout.write(f'テキストファイルパス: {txt_path}')
        self.stdout.write(f'画像ディレクトリ: {image_dir}')

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
                # 正の問題番号を処理
                if number < 1:
                    continue
                self.stdout.write(f'処理中の問題番号: {number}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'問題番号の取得に失敗: {e}'))
                continue

            # 画像・音声ファイル名
            image_name = f'listening_illustration_image{number}.png'
            audio_name = f'listening_illustration_question{number}.mp3'
            image_path = db_image_path_part1(level, image_name)
            audio_part = listening_illustration_audio_part(level, number)
            audio_path = db_audio_path(level, audio_part, audio_name)

            self.stdout.write(f'画像ファイル: {image_path}')
            self.stdout.write(f'音声ファイル: {audio_path} ({audio_part})')

            # 選択肢・正解・解説の抽出
            choices = []
            correct_answer = ''
            explanation = ''
            in_choices = False
            in_explanation = False
            
            for line in lines[1:]:
                if line.strip().startswith('Question No.'):
                    in_choices = True
                    continue
                if in_choices and line.strip() and not line.startswith('【'):
                    stripped = line.strip()
                    if len(stripped) >= 2 and stripped[0].isdigit() and stripped[1] == '.':
                        choices.append(stripped[3:].strip())
                if '【正解' in line:
                    in_choices = False
                    # 正解テキストを抽出（次の行から）
                    continue
                if '【解説' in line:
                    in_explanation = True
                    explanation = ''
                    continue
                if in_explanation:
                    if line.strip().startswith('---'):
                        in_explanation = False
                    else:
                        explanation += line.strip() + '\n'
                elif not in_choices and not in_explanation and line.strip() and not line.startswith('【'):
                    stripped = line.strip()
                    if len(stripped) >= 2 and stripped[0].isdigit() and stripped[1] == '.':
                        # 番号を抽出（例：「2. I have a piano lesson.」→「2」）
                        correct_answer_order = int(line.strip()[0])
                        correct_answer_text = line.strip()[3:].strip()
                        correct_answer = str(correct_answer_order)  # order番号を文字列で保存
                    else:
                        correct_answer = line.strip()
            
            explanation = explanation.strip()

            # モデル登録
            q = ListeningQuestion.objects.create(
                question_text='',
                image=image_path,
                audio=audio_path,
                correct_answer=correct_answer,
                explanation=explanation,
                level=level
            )

            # 選択肢を番号で登録（既存の形式に合わせる）
            # correct_answerはorder番号（文字列）になっている
            correct_order = int(correct_answer) if correct_answer.isdigit() else None
            is_level5_part3 = level == '5' and number >= 31

            for i, choice_text in enumerate(choices, 1):
                if is_level5_part3:
                    choice_img = f'listening_illustration_q{number}_choice{i}.png'
                    stored_text = db_image_path_part1(level, choice_img)
                else:
                    stored_text = str(i)
                ListeningChoice.objects.create(
                    question=q,
                    choice_text=stored_text,
                    is_correct=(i == correct_order) if correct_order else False,
                    order=i,
                )

            self.stdout.write(self.style.SUCCESS(f'問題 No.{number} を登録（選択肢{len(choices)}個, 正解: {correct_answer}）'))

        self.stdout.write(self.style.SUCCESS(
            f'イラストリスニング問題の登録が完了しました（level={level}）'
        )) 