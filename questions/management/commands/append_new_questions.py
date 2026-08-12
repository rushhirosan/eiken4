"""
既存問題を消さず、テキストにある未登録番号だけ追加する。
4級 / 3級の新規回次追記登録用（進捗安全）。
"""
from __future__ import annotations

import re
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from exams.models import Choice, Question
from exams.provenance import PROVENANCE_BLOCKED
from exams.writing_feedback import parse_writing_rubric
from questions.level_paths import (
    db_audio_path,
    db_image_path_part1,
    questions_file_abspath,
)
from questions.models import (
    ListeningChoice,
    ListeningQuestion,
    ReadingChoice,
    ReadingPassage,
    ReadingQuestion,
)

# 3級 2026① / 4級 2026① の既定下限（--min-* 未指定時）
_DEFAULT_MINS = {
    '3': {
        'min_grammar': 101,
        'min_conversation': 51,
        'min_wordorder': 9999,  # 3級に語順なし
        'min_reading_passage': 16,
        'min_listening': 41,
        'min_writing': 21,
    },
    '4': {
        'min_grammar': 166,
        'min_conversation': 56,
        'min_wordorder': 26,
        'min_reading_passage': 13,
        'min_listening': 41,
        'min_writing': 9999,  # 4級にライティングなし
    },
}


class Command(BaseCommand):
    help = 'テキストの新規番号だけ追加登録（既存削除なし・進捗安全）'

    def add_arguments(self, parser):
        parser.add_argument('--level', default='4')
        parser.add_argument(
            '--min-grammar',
            type=int,
            default=None,
            help='この番号以上の grammar_fill を追加',
        )
        parser.add_argument('--min-conversation', type=int, default=None)
        parser.add_argument('--min-wordorder', type=int, default=None)
        parser.add_argument('--min-reading-passage', type=int, default=None)
        parser.add_argument('--min-listening', type=int, default=None)
        parser.add_argument('--min-writing', type=int, default=None)
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        level = str(options['level'])
        dry = options['dry_run']
        defaults = _DEFAULT_MINS.get(level, _DEFAULT_MINS['4'])

        def pick(key: str) -> int:
            val = options[key]
            return defaults[key] if val is None else val

        min_grammar = pick('min_grammar')
        min_conversation = pick('min_conversation')
        min_wordorder = pick('min_wordorder')
        min_reading = pick('min_reading_passage')
        min_listening = pick('min_listening')
        min_writing = pick('min_writing')

        with transaction.atomic():
            self._append_choice_questions(
                level,
                'grammar_fill',
                'grammar_fill_questions.txt',
                min_grammar,
                dry,
            )
            self._append_choice_questions(
                level,
                'conversation_fill',
                'conversation_questions.txt',
                min_conversation,
                dry,
            )
            wordorder_path = Path(questions_file_abspath(level, 'wordorder_questions.txt'))
            if wordorder_path.exists() and min_wordorder < 9000:
                self._append_choice_questions(
                    level,
                    'word_order',
                    'wordorder_questions.txt',
                    min_wordorder,
                    dry,
                )
            else:
                self.stdout.write('word_order: skipped')
            self._append_reading(level, min_reading, dry)
            if min_writing < 9000:
                self._append_writing(level, min_writing, dry)
            else:
                self.stdout.write('writing: skipped')
            self._append_listening_illustration(level, min_listening, dry)
            self._append_listening_exam_type(
                level,
                'listening_conversation',
                'listening_conversation_questions.txt',
                'part2',
                'listening_conversation_question',
                min_listening,
                dry,
            )
            # 5級の part3 はイラスト一致のため listening_passage ファイルが無い場合あり
            passage_path = Path(
                questions_file_abspath(level, 'listening_passage_questions.txt')
            )
            if passage_path.exists():
                self._append_listening_exam_type(
                    level,
                    'listening_passage',
                    'listening_passage_questions.txt',
                    'part3',
                    'listening_passage_question',
                    min_listening,
                    dry,
                )
            if dry:
                transaction.set_rollback(True)
                self.stdout.write(self.style.WARNING('dry-run: rollback'))
                return

    def _append_choice_questions(self, level, qtype, filename, min_n, dry):
        path = Path(questions_file_abspath(level, filename))
        content = path.read_text(encoding='utf-8')
        existing = set(
            Question.objects.filter(level=level, question_type=qtype).values_list(
                'question_number', flat=True
            )
        )
        added = 0
        for block in content.split('---'):
            if not block.strip():
                continue
            m = re.search(r'問題(\d+)', block)
            if not m:
                continue
            n = int(m.group(1))
            if n < min_n or n in existing:
                continue
            q_match = re.search(r'問題\d+.*?:\s*(.*?)\s*選択肢\d+:', block, re.DOTALL)
            c_match = re.search(r'選択肢\d+:\s*(.*?)\s*【正解\d+】', block, re.DOTALL)
            a_match = re.search(r'【正解\d+】\s*(\d+)\.', block)
            e_match = re.search(r'【解説\d+】\s*(.*?)(?=\n\n---|$)', block, re.DOTALL)
            if not (q_match and c_match and a_match):
                self.stdout.write(self.style.WARNING(f'skip parse {qtype} #{n}'))
                continue
            choices = []
            for line in c_match.group(1).splitlines():
                line = line.strip()
                if re.match(r'^\d+\.', line):
                    choices.append(re.sub(r'^\d+\.\s*', '', line))
            ans = int(a_match.group(1))
            expl = e_match.group(1).strip() if e_match else ''
            if dry:
                self.stdout.write(f'[dry] {qtype} #{n}')
            else:
                q = Question.objects.create(
                    provenance=PROVENANCE_BLOCKED,
                    level=level,
                    question_type=qtype,
                    question_text=q_match.group(1).strip(),
                    explanation=expl,
                    question_number=n,
                )
                for order, text in enumerate(choices, 1):
                    Choice.objects.create(
                        question=q,
                        choice_text=text,
                        is_correct=(order == ans),
                        order=order,
                    )
            added += 1
        self.stdout.write(self.style.SUCCESS(f'{qtype}: +{added}'))

    def _append_writing(self, level, min_n, dry):
        path = Path(questions_file_abspath(level, 'writing_questions.txt'))
        if not path.exists():
            self.stdout.write('writing: no file')
            return
        content = path.read_text(encoding='utf-8')
        existing = set(
            Question.objects.filter(level=level, question_type='writing').values_list(
                'question_number', flat=True
            )
        )
        added = 0
        for block in content.split('---'):
            if not block.strip():
                continue
            m = re.search(r'問題(\d+):', block)
            if not m:
                continue
            n = int(m.group(1))
            if n < min_n or n in existing:
                continue
            body_match = re.search(
                rf'問題{n}:\s*(.*?)\s*【参考解答】\s*',
                block,
                re.DOTALL,
            )
            expl_match = re.search(
                r'【参考解答】\s*(.*?)(?=\n※協会|\Z)',
                block,
                re.DOTALL,
            )
            if not body_match:
                self.stdout.write(self.style.WARNING(f'skip parse writing #{n}'))
                continue
            q_text = body_match.group(1).strip()
            expl = expl_match.group(1).strip() if expl_match else ''
            if dry:
                self.stdout.write(f'[dry] writing #{n}')
            else:
                Question.objects.create(
                    provenance=PROVENANCE_BLOCKED,
                    level=level,
                    question_type='writing',
                    question_text=q_text,
                    explanation=expl,
                    question_number=n,
                    writing_rubric=parse_writing_rubric(q_text),
                )
            added += 1
        self.stdout.write(self.style.SUCCESS(f'writing: +{added}'))

    def _append_reading(self, level, min_passage, dry):
        path = Path(questions_file_abspath(level, 'reading_comprehesion_questions.txt'))
        content = path.read_text(encoding='utf-8')
        # identifier は CharField(max_length=1) のため a–z のみ
        id_map = {
            i: chr(ord('a') + i - 1) for i in range(1, 27)
        }
        existing_ids = set(
            ReadingPassage.objects.filter(level=level).values_list('identifier', flat=True)
        )
        added_p = added_q = 0
        for block in content.split('---'):
            if not block.strip():
                continue
            pm = re.search(r'本文(\d+)', block)
            if not pm:
                continue
            pnum = int(pm.group(1))
            if pnum < min_passage:
                continue
            ident = id_map.get(pnum)
            if not ident or ident in existing_ids:
                continue
            p_match = re.search(r'本文\d+\s*\n(.*?)(?=\n問題\d+[a-z]:)', block, re.DOTALL)
            if not p_match:
                continue
            if dry:
                self.stdout.write(f'[dry] reading passage {pnum}')
                passage = None
            else:
                passage = ReadingPassage.objects.create(
                    provenance=PROVENANCE_BLOCKED,
                    text=p_match.group(1).strip(),
                    level=level,
                    identifier=ident,
                )
            added_p += 1
            q_iter = re.finditer(
                r'問題\d+[a-z]:\s*(.*?)\n選択肢\d+[a-z]:\s*(.*?)\n【正解\d+[a-z]】\s*(.*?)\n【解説\d+[a-z]】\s*(.*?)(?=\n問題\d+[a-z]:|\n---|$)',
                block,
                re.DOTALL,
            )
            for i, qm in enumerate(q_iter, 1):
                q_text = qm.group(1).strip()
                choices_text = qm.group(2).strip()
                correct = qm.group(3).strip()
                expl = qm.group(4).strip()
                if correct.startswith(('1.', '2.', '3.', '4.')):
                    correct = correct[2:].strip()
                if dry:
                    added_q += 1
                    continue
                rq = ReadingQuestion.objects.create(
                    provenance=PROVENANCE_BLOCKED,
                    passage=passage,
                    question_text=q_text,
                    question_number=i,
                    explanation=expl,
                )
                for order, line in enumerate(
                    [c.strip() for c in choices_text.split('\n') if c.strip()], 1
                ):
                    ct = line[2:].strip() if line.startswith(('1.', '2.', '3.', '4.')) else line
                    ReadingChoice.objects.create(
                        question=rq,
                        choice_text=ct,
                        is_correct=(ct == correct),
                        order=order,
                    )
                added_q += 1
        self.stdout.write(self.style.SUCCESS(f'reading: +{added_p} passages / +{added_q} qs'))

    def _append_listening_illustration(self, level, min_n, dry):
        path = Path(questions_file_abspath(level, 'listening_illustration_questions.txt'))
        content = path.read_text(encoding='utf-8')
        blocks = []
        cur = []
        for line in content.split('\n'):
            if line.strip().startswith('No.'):
                if cur:
                    blocks.append('\n'.join(cur))
                cur = [line]
            else:
                cur.append(line)
        if cur:
            blocks.append('\n'.join(cur))

        existing = set()
        for lq in ListeningQuestion.objects.filter(level=level):
            m = re.search(r'listening_illustration_image(\d+)\.png', lq.image or '')
            if m:
                existing.add(int(m.group(1)))

        added = 0
        for block in blocks:
            lines = [l for l in block.split('\n') if l.strip()]
            if not lines:
                continue
            try:
                n = int(lines[0].replace('No.', '').replace(':', '').strip())
            except ValueError:
                continue
            if n < min_n or n in existing:
                continue
            # dialogue until Question No.
            dialog_lines = []
            choices = []
            mode = 'dialog'
            for line in lines[1:]:
                s = line.strip()
                if s.startswith('Question No.'):
                    mode = 'choices'
                    continue
                if s.startswith('【正解'):
                    break
                if mode == 'dialog':
                    dialog_lines.append(s)
                elif re.match(r'^\d+\.', s):
                    choices.append(re.sub(r'^\d+\.\s*', '', s))
            a_match = re.search(r'【正解\d+】\s*(\d+)\.', block)
            e_match = re.search(r'【解説\d+】\s*(.*?)(?=\n---|$)', block, re.DOTALL)
            if not a_match or len(choices) != 3:
                self.stdout.write(self.style.WARNING(f'skip ill #{n}'))
                continue
            ans = int(a_match.group(1))
            expl = e_match.group(1).strip() if e_match else ''
            image = db_image_path_part1(level, f'listening_illustration_image{n}.png')
            audio = db_audio_path(level, 'part1', f'listening_illustration_question{n}.mp3')
            if dry:
                self.stdout.write(f'[dry] listening_illustration #{n}')
            else:
                # register_listening_illustration_questions と同じ: 本文空、選択肢は番号文字
                lq = ListeningQuestion.objects.create(
                    provenance=PROVENANCE_BLOCKED,
                    level=level,
                    question_text='',
                    explanation=expl,
                    image=image,
                    audio=audio,
                    correct_answer=str(ans),
                )
                for order, _text in enumerate(choices, 1):
                    ListeningChoice.objects.create(
                        question=lq,
                        choice_text=str(order),
                        is_correct=(order == ans),
                        order=order,
                    )
            added += 1
        self.stdout.write(self.style.SUCCESS(f'listening_illustration: +{added}'))

    def _append_listening_exam_type(
        self, level, qtype, filename, part, audio_prefix, min_n, dry
    ):
        path = Path(questions_file_abspath(level, filename))
        content = path.read_text(encoding='utf-8')
        existing = set(
            Question.objects.filter(level=level, question_type=qtype).values_list(
                'question_number', flat=True
            )
        )
        added = 0
        for block in content.split('---'):
            if not block.strip():
                continue
            nm = re.search(r'No\.(\d+):', block)
            if not nm:
                continue
            n = int(nm.group(1))
            if n < min_n or n in existing:
                continue
            conv = re.search(r'No\.\d+:\n(.*?)\n\nQuestion', block, re.DOTALL)
            qm = re.search(r'Question No\.\d+:\s*(.*?)\n', block)
            am = re.search(r'【正解\d+】\s*(\d+)\.', block)
            em = re.search(r'【解説\d+】\s*(.*?)(?=\n---|$)', block, re.DOTALL)
            if not (conv and qm and am):
                self.stdout.write(self.style.WARNING(f'skip {qtype} #{n}'))
                continue
            choices = []
            after_q = False
            q_text = qm.group(1).strip()
            for line in block.split('\n'):
                if line.strip() == q_text or line.strip().startswith('Question No.'):
                    after_q = True
                    continue
                if after_q and re.match(r'^\d+\.', line.strip()):
                    choices.append(re.sub(r'^\d+\.\s*', '', line.strip()))
                    if len(choices) == 4:
                        break
                if '【正解' in line:
                    break
            if len(choices) != 4:
                self.stdout.write(self.style.WARNING(f'skip choices {qtype} #{n}'))
                continue
            ans = int(am.group(1))
            expl = em.group(1).strip() if em else ''
            af = db_audio_path(level, part, f'{audio_prefix}{n}.mp3')
            if dry:
                self.stdout.write(f'[dry] {qtype} #{n}')
            else:
                q = Question.objects.create(
                    provenance=PROVENANCE_BLOCKED,
                    level=level,
                    question_type=qtype,
                    question_text=q_text,
                    listening_text=conv.group(1).strip(),
                    explanation=expl,
                    audio_file=af,
                    question_number=n,
                )
                for order, text in enumerate(choices, 1):
                    Choice.objects.create(
                        question=q,
                        choice_text=text,
                        is_correct=(order == ans),
                        order=order,
                    )
            added += 1
        self.stdout.write(self.style.SUCCESS(f'{qtype}: +{added}'))
