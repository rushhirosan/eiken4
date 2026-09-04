from django.core.management.base import BaseCommand
from questions.models import ReadingPassage, ReadingQuestion, ReadingChoice
import re

from questions.level_paths import add_default_register_arguments
from questions.register_source import resolve_register_io
from questions.study_points import extract_explanation, extract_study_points


class Command(BaseCommand):
    help = 'Register reading comprehension passages and questions from text file'

    def add_arguments(self, parser):
        add_default_register_arguments(parser)

    def handle(self, *args, **options):
        level, txt_path, provenance, is_original = resolve_register_io(
            options, 'reading_comprehesion_questions.txt'
        )
        qs = ReadingPassage.objects.filter(level=level)
        if is_original:
            qs = qs.filter(provenance=provenance)
        qs.delete()
        scope = 'original' if is_original else '全件'
        self.stdout.write(
            self.style.WARNING(f'既存の読解パッセージ（level={level}, {scope}）を削除しました')
        )

        with open(txt_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Split into passages
        passages = content.split('---')

        for passage_block in passages:
            if not passage_block.strip():
                continue

            # Extract passage number
            passage_number_match = re.search(r'本文(\d+)', passage_block)
            if not passage_number_match:
                continue
            passage_number = int(passage_number_match.group(1))

            # Process passages 1-15 (level 3 may have up to 15)
            if passage_number < 1 or passage_number > 15:
                continue

            # Extract passage text (everything from 本文 to the first question)
            passage_match = re.search(r'本文\d+\s*\n(.*?)(?=\n問題\d+[a-z]:)', passage_block, re.DOTALL)
            if not passage_match:
                continue
            passage_text = passage_match.group(1).strip()

            # Create passage
            # Convert passage number to single character identifier (1->a … 15->o)
            identifier_map = {
                1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f', 7: 'g', 8: 'h',
                9: 'i', 10: 'j', 11: 'k', 12: 'l', 13: 'm', 14: 'n', 15: 'o',
            }
            identifier = identifier_map.get(passage_number, 'a')

            passage = ReadingPassage.objects.create(
                provenance=provenance,
                text=passage_text,
                level=level,
                identifier=identifier
            )

            # Extract all questions for this passage
            question_iter = re.finditer(
                r'(問題(\d+[a-z]):.*?)(?=\n問題\d+[a-z]:|\Z)',
                passage_block,
                re.DOTALL,
            )

            question_count = 0
            for i, question_match in enumerate(question_iter, 1):
                question_block = question_match.group(1)
                suffix = question_match.group(2)

                q_text_match = re.search(
                    rf'問題{re.escape(suffix)}:\s*(.*?)\s*選択肢{re.escape(suffix)}:',
                    question_block,
                    re.DOTALL,
                )
                choices_match = re.search(
                    rf'選択肢{re.escape(suffix)}:\s*(.*?)\s*【正解{re.escape(suffix)}】',
                    question_block,
                    re.DOTALL,
                )
                correct_match = re.search(
                    rf'【正解{re.escape(suffix)}】\s*(.*?)\s*【解説{re.escape(suffix)}】',
                    question_block,
                    re.DOTALL,
                )
                if not (q_text_match and choices_match and correct_match):
                    self.stdout.write(
                        self.style.WARNING(
                            f'本文{passage_number} 問題{suffix}: パースできませんでした'
                        )
                    )
                    continue

                question_text = q_text_match.group(1).strip()
                choices_text = choices_match.group(1).strip()
                correct_answer = correct_match.group(1).strip()
                explanation = extract_explanation(question_block, suffix=re.escape(suffix))
                study_points = extract_study_points(question_block, suffix=re.escape(suffix))

                # 正解の番号を除去（例：「3. Go fishing」→「Go fishing」）
                if correct_answer.startswith(('1.', '2.', '3.', '4.')):
                    correct_answer = correct_answer[2:].strip()

                # Create question
                question = ReadingQuestion.objects.create(
                    passage=passage,
                    question_text=question_text,
                    question_number=i,
                    explanation=explanation,
                    study_points=study_points,
                )

                # Create choices
                choices = [c.strip() for c in choices_text.split('\n') if c.strip()]
                for order, choice_text in enumerate(choices, 1):
                    # 選択肢の番号を除去（例：「3. Go fishing」→「Go fishing」）
                    if choice_text.startswith(('1.', '2.', '3.', '4.')):
                        choice_text = choice_text[2:].strip()
                    is_correct = choice_text == correct_answer

                    ReadingChoice.objects.create(
                        question=question,
                        choice_text=choice_text,
                        is_correct=is_correct,
                        order=order
                    )
                question_count += 1

            self.stdout.write(self.style.SUCCESS(f'本文{passage_number}と{question_count}問の問題を登録しました'))

        self.stdout.write(self.style.SUCCESS('登録完了'))

        # 確認
        total_passages = ReadingPassage.objects.filter(level=level).count()
        total_questions = ReadingQuestion.objects.filter(passage__level=level).count()
        self.stdout.write(self.style.SUCCESS(
            f'データベース内の読解問題総数（level={level}）: 本文{total_passages}個、問題{total_questions}問'
        ))
