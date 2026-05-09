import re

from django.core.management.base import BaseCommand

from exams.models import Question

from questions.level_paths import (
    add_default_register_arguments,
    questions_file_abspath,
)


class Command(BaseCommand):
    help = 'ライティング問題をテキストファイルから登録する（選択肢なし・参考解答は explanation）'

    def add_arguments(self, parser):
        add_default_register_arguments(parser)

    def handle(self, *args, **options):
        level = options['level']
        Question.objects.filter(question_type='writing', level=level).delete()
        self.stdout.write(
            self.style.WARNING(f'既存のライティング問題（level={level}）を削除しました')
        )

        txt_path = questions_file_abspath(level, 'writing_questions.txt')
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()

        blocks = content.split('---')
        registered = 0
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            m_num = re.search(r'問題(\d+):', block)
            if not m_num:
                continue
            qn = int(m_num.group(1))
            if qn < 1 or qn > 99:
                continue

            # 問題文: このブロック先頭の「問題qn:」から 【参考解答】 まで（別の「問題\d+:」が紛れても取り違えない）
            body_match = re.search(
                rf'問題{qn}:\s*(.*?)\s*【参考解答】\s*',
                block,
                re.DOTALL,
            )
            if not body_match:
                self.stdout.write(
                    self.style.WARNING(f'問題{qn}: 本文を抽出できませんでした')
                )
                continue
            question_text = body_match.group(1).strip()

            # 参考解答は「※協会…」の手前まで（ブロック結合ミスで次問が混入するのを防ぐ）
            ref_match = re.search(
                r'【参考解答】\s*(.*?)(?=\n※協会|\Z)',
                block,
                re.DOTALL,
            )
            explanation = ref_match.group(1).strip() if ref_match else ''

            Question.objects.create(
                question_text=question_text,
                level=level,
                question_type='writing',
                question_number=qn,
                explanation=explanation,
            )
            registered += 1
            self.stdout.write(
                self.style.SUCCESS(f'問題{qn}を登録しました')
            )

        self.stdout.write(
            self.style.SUCCESS(f'\n登録完了: {registered}問')
        )
