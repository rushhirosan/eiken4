import re

from django.core.management.base import BaseCommand

from exams.models import Question
from exams.provenance import PROVENANCE_BLOCKED
from questions.legacy_import import assert_legacy_question_import_allowed
from questions.level_paths import (
    add_default_register_arguments,
    questions_file_abspath,
)

_KIND_RE = re.compile(
    r'^(\d+)\.\s*(?:\[(passage|illustration|personal)\]\s*)?(.+)$'
)


def _infer_kind(level: str, number: int) -> str:
    """級と番号から質問種別を推定（タグ省略時）。"""
    level = str(level)
    if level == '5':
        return 'personal' if number >= 3 else 'passage'
    if level == '4':
        if number <= 2:
            return 'passage'
        if number == 3:
            return 'illustration'
        return 'personal'
    # 3級二次
    if number == 1:
        return 'passage'
    if number in (2, 3):
        return 'illustration'
    return 'personal'


def _parse_speaking_block(block: str, qn: int, level: str):
    """1ブロックから title / passage / illustration / questions / explanation を取り出す。"""
    title_m = re.search(
        r'【Title】\s*(.*?)\s*【Passage】',
        block,
        re.DOTALL,
    )
    passage_m = re.search(
        r'【Passage】\s*(.*?)\s*(?:【Illustration】|【Questions】)',
        block,
        re.DOTALL,
    )
    illustration_m = re.search(
        r'【Illustration】\s*(.*?)\s*【Questions】',
        block,
        re.DOTALL,
    )
    questions_m = re.search(
        r'【Questions】\s*(.*?)\s*【参考解答】',
        block,
        re.DOTALL,
    )
    explanation_m = re.search(
        r'【参考解答】\s*(.*)\Z',
        block,
        re.DOTALL,
    )
    if not (title_m and passage_m and questions_m):
        return None

    title = title_m.group(1).strip()
    passage = passage_m.group(1).strip()
    illustration = illustration_m.group(1).strip() if illustration_m else ''
    explanation = explanation_m.group(1).strip() if explanation_m else ''

    prompts = []
    for line in questions_m.group(1).splitlines():
        line = line.strip()
        if not line:
            continue
        qm = _KIND_RE.match(line)
        if not qm:
            continue
        number = int(qm.group(1))
        kind = qm.group(2) or _infer_kind(level, number)
        prompts.append({
            'number': number,
            'prompt': qm.group(3).strip(),
            'kind': kind,
            'personal': kind == 'personal',
        })

    sample_by_num = {}
    for line in explanation.splitlines():
        sm = re.match(r'^(\d+)\.\s*(.+)$', line.strip())
        if not sm:
            continue
        num = int(sm.group(1))
        answers = [a.strip() for a in sm.group(2).split('/') if a.strip()]
        sample_by_num[num] = answers

    for item in prompts:
        item['sample_answers'] = sample_by_num.get(item['number'], [])

    turn_over_after = 3 if str(level) == '3' else None
    speaking_data = {
        'title': title,
        'passage': passage,
        'illustration': illustration,
        'silent_seconds': 20,
        'turn_over_after': turn_over_after,
        'questions': prompts,
    }
    question_text = f'{title}\n\n{passage}'
    if illustration:
        question_text += f'\n\n[Illustration]\n{illustration}'
    return question_text, explanation, speaking_data


class Command(BaseCommand):
    help = 'スピーキング問題をテキストから登録する（採点なし・参考解答は explanation）'

    def add_arguments(self, parser):
        add_default_register_arguments(parser)

    def handle(self, *args, **options):
        assert_legacy_question_import_allowed(allow_flag=options.get('allow_legacy_blocked_import', False))
        level = options['level']
        if level not in ('3', '4', '5'):
            self.stdout.write(
                self.style.ERROR(f'スピーキングは level 3/4/5 のみ対応です: {level}')
            )
            return

        Question.objects.filter(question_type='speaking', level=level).delete()
        self.stdout.write(
            self.style.WARNING(f'既存のスピーキング問題（level={level}）を削除しました')
        )

        txt_path = questions_file_abspath(level, 'speaking_questions.txt')
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
            parsed = _parse_speaking_block(block, qn, level)
            if not parsed:
                self.stdout.write(
                    self.style.WARNING(f'問題{qn}: 解析できませんでした')
                )
                continue
            question_text, explanation, speaking_data = parsed
            Question.objects.create(
                    provenance=PROVENANCE_BLOCKED,
                question_text=question_text,
                level=level,
                question_type='speaking',
                question_number=qn,
                explanation=explanation,
                speaking_data=speaking_data,
            )
            registered += 1
            self.stdout.write(self.style.SUCCESS(f'問題{qn}を登録しました'))

        self.stdout.write(self.style.SUCCESS(f'\n登録完了: {registered}問（level={level}）'))
