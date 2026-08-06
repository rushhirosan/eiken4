import re

from django.core.management.base import BaseCommand

from exams.models import Question
from questions.level_paths import (
    add_default_register_arguments,
    questions_file_abspath,
)


def _parse_speaking_block(block: str, qn: int):
    """1ブロックから title / passage / questions / explanation を取り出す。"""
    title_m = re.search(
        r'【Title】\s*(.*?)\s*【Passage】',
        block,
        re.DOTALL,
    )
    passage_m = re.search(
        r'【Passage】\s*(.*?)\s*【Questions】',
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
    explanation = explanation_m.group(1).strip() if explanation_m else ''

    prompts = []
    for line in questions_m.group(1).splitlines():
        line = line.strip()
        if not line:
            continue
        qm = re.match(r'^(\d+)\.\s*(.+)$', line)
        if qm:
            prompts.append({
                'number': int(qm.group(1)),
                'prompt': qm.group(2).strip(),
                'personal': int(qm.group(1)) >= 3,
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

    speaking_data = {
        'title': title,
        'passage': passage,
        'silent_seconds': 20,
        'questions': prompts,
    }
    # 一覧表示用に title + passage を question_text に入れる
    question_text = f'{title}\n\n{passage}'
    return question_text, explanation, speaking_data


class Command(BaseCommand):
    help = 'スピーキング問題をテキストから登録する（採点なし・参考解答は explanation）'

    def add_arguments(self, parser):
        add_default_register_arguments(parser)

    def handle(self, *args, **options):
        level = options['level']
        if level != '5':
            self.stdout.write(
                self.style.WARNING(
                    f'現在スピーキング問題データは5級のみです（指定: level={level}）'
                )
            )

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
            parsed = _parse_speaking_block(block, qn)
            if not parsed:
                self.stdout.write(
                    self.style.WARNING(f'問題{qn}: 解析できませんでした')
                )
                continue
            question_text, explanation, speaking_data = parsed
            Question.objects.create(
                question_text=question_text,
                level=level,
                question_type='speaking',
                question_number=qn,
                explanation=explanation,
                speaking_data=speaking_data,
            )
            registered += 1
            self.stdout.write(self.style.SUCCESS(f'問題{qn}を登録しました'))

        self.stdout.write(self.style.SUCCESS(f'\n登録完了: {registered}問'))
