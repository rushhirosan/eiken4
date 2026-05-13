import re

from django.core.management.base import BaseCommand

from exams.models import Question

from questions.level_paths import (
    add_default_register_arguments,
    questions_file_abspath,
)

# 本文・参考解答から除く行（テキストに残っていても登録時に落とす）
# 例: 【2025年度第1回・問題4・メール返信】、【出典】のみの行 など
_LINE_FULLWIDTH_BRACKETS = re.compile(r'^【[^】]*】\s*$')
_LINE_KYOKAI_DISCLAIMER = re.compile(
    r'^※協会発表の解答例（一次試験）より[。.]?\s*$',
)


def _strip_block_leader_metadata(block: str) -> str:
    """ブロック先頭の空行と【…】のみの行・協会注意書きを除く（問題n: の手前の出典メタ用）。"""
    lines = block.splitlines()
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        if _LINE_FULLWIDTH_BRACKETS.match(s) or _LINE_KYOKAI_DISCLAIMER.match(s):
            i += 1
            continue
        break
    return '\n'.join(lines[i:]).strip()


def _strip_writing_noise_lines(text: str) -> str:
    """【…】のみの行（回次・問題番号のメタ含む）と協会注意書きの行を除く。"""
    out: list[str] = []
    for line in text.splitlines():
        s = line.strip()
        if _LINE_FULLWIDTH_BRACKETS.match(s) or _LINE_KYOKAI_DISCLAIMER.match(s):
            continue
        out.append(line)
    return '\n'.join(out).strip()


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
            block = _strip_block_leader_metadata(block.strip())
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
            question_text = _strip_writing_noise_lines(body_match.group(1).strip())

            # 参考解答は「※協会…」の手前まで（ブロック結合ミスで次問が混入するのを防ぐ）
            ref_match = re.search(
                r'【参考解答】\s*(.*?)(?=\n※協会|\Z)',
                block,
                re.DOTALL,
            )
            explanation = _strip_writing_noise_lines(
                ref_match.group(1).strip() if ref_match else ''
            )

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
