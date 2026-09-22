import re

from django.core.management.base import BaseCommand

from exams.models import Question
from questions.level_paths import add_default_register_arguments
from questions.register_source import resolve_register_io
from questions.study_points import extract_study_points

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
        r'【参考解答】\s*(.*?)(?=\n*【ポイント|\Z)',
        block,
        re.DOTALL,
    )
    if not (title_m and passage_m and questions_m):
        return None

    title = title_m.group(1).strip()
    passage = passage_m.group(1).strip()
    illustration = illustration_m.group(1).strip() if illustration_m else ''
    explanation = explanation_m.group(1).strip() if explanation_m else ''
    study_points = extract_study_points(block)

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
    return question_text, explanation, speaking_data, study_points


class Command(BaseCommand):
    help = (
        'スピーキング問題をテキストから登録する（採点なし・参考解答は explanation）。'
        '--in-place なら既存行を question_number で更新し、回答・進捗を保持する。'
    )

    def add_arguments(self, parser):
        add_default_register_arguments(parser)
        parser.add_argument(
            '--in-place',
            action='store_true',
            help=(
                '既存の speaking 行を削除せず、同番号を更新する。'
                'SpeakingUserAnswer など進捗を残したいときに使う。'
            ),
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='DBを更新せず、解析・対象件数だけ表示する',
        )

    def handle(self, *args, **options):
        level, txt_path, provenance, is_original = resolve_register_io(
            options, 'speaking_questions.txt'
        )
        if level not in ('3', '4', '5'):
            self.stdout.write(
                self.style.ERROR(f'スピーキングは level 3/4/5 のみ対応です: {level}')
            )
            return

        in_place = options['in_place']
        dry_run = options['dry_run']
        scope = 'original' if is_original else '全件'

        if not in_place:
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f'[dry-run] 既存のスピーキング問題（level={level}, {scope}）を削除する予定'
                    )
                )
            else:
                qs = Question.objects.filter(question_type='speaking', level=level)
                if is_original:
                    qs = qs.filter(provenance=provenance)
                qs.delete()
                self.stdout.write(
                    self.style.WARNING(
                        f'既存のスピーキング問題（level={level}, {scope}）を削除しました'
                    )
                )

        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()

        blocks = content.split('---')
        registered = 0
        updated = 0
        created = 0
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
            question_text, explanation, speaking_data, study_points = parsed
            fields = {
                'question_text': question_text,
                'explanation': explanation,
                'speaking_data': speaking_data,
                'study_points': study_points,
            }

            if in_place:
                lookup = {
                    'question_type': 'speaking',
                    'level': level,
                    'question_number': qn,
                    'provenance': provenance,
                }
                existing = Question.objects.filter(**lookup).first()
                if existing is None:
                    created += 1
                    if dry_run:
                        self.stdout.write(
                            f'[dry-run] 問題{qn}: 既存なし → create 予定'
                        )
                    else:
                        Question.objects.create(
                            provenance=provenance,
                            level=level,
                            question_type='speaking',
                            question_number=qn,
                            **fields,
                        )
                        self.stdout.write(
                            self.style.SUCCESS(f'問題{qn}を新規登録しました（in-place）')
                        )
                else:
                    updated += 1
                    if dry_run:
                        self.stdout.write(f'[dry-run] 問題{qn}: update 予定 id={existing.id}')
                    else:
                        for key, value in fields.items():
                            setattr(existing, key, value)
                        existing.save(update_fields=list(fields.keys()))
                        self.stdout.write(
                            self.style.SUCCESS(f'問題{qn}を更新しました（id={existing.id}）')
                        )
                registered += 1
                continue

            if dry_run:
                self.stdout.write(f'[dry-run] 問題{qn}: create 予定')
            else:
                Question.objects.create(
                    provenance=provenance,
                    question_text=question_text,
                    level=level,
                    question_type='speaking',
                    question_number=qn,
                    explanation=explanation,
                    speaking_data=speaking_data,
                    study_points=study_points,
                )
                self.stdout.write(self.style.SUCCESS(f'問題{qn}を登録しました'))
            registered += 1

        if in_place:
            action = 'would sync' if dry_run else 'sync'
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n{action}: {registered}問（update={updated}, create={created}, '
                    f'level={level}, in-place）'
                )
            )
        else:
            action = 'would register' if dry_run else '登録完了'
            self.stdout.write(
                self.style.SUCCESS(f'\n{action}: {registered}問（level={level}）')
            )
