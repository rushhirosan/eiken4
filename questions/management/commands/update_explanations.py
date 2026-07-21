"""Update question explanations from txt without deleting rows (progress-safe)."""

from django.core.management.base import BaseCommand, CommandError

from questions.explanation_sync import CATEGORIES, sync_explanations
from questions.level_paths import add_default_register_arguments


class Command(BaseCommand):
    help = (
        'data/questions の【解説】（ライティングは【参考解答】）だけを既存DBへ反映する。'
        '問題行は削除しないので回答・進捗を保持する。'
    )

    def add_arguments(self, parser):
        add_default_register_arguments(parser)
        parser.add_argument(
            '--category',
            required=True,
            choices=sorted(CATEGORIES.keys()),
            help=(
                '更新カテゴリ。listening=リスニング3パート、all=全カテゴリ。'
                '個別: grammar_fill, conversation_fill, word_order, '
                'reading_comprehension, writing, listening_illustration, '
                'listening_conversation, listening_passage'
            ),
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='DBを更新せず件数だけ表示',
        )

    def handle(self, *args, **options):
        level = options['level']
        category = options['category']
        dry_run = options['dry_run']

        self.stdout.write(
            f'explanation sync: level={level}, category={category}, '
            f'dry_run={dry_run}'
        )

        try:
            results = sync_explanations(
                level=level,
                category=category,
                dry_run=dry_run,
                log=self.stdout.write,
                warn=lambda msg: self.stdout.write(self.style.WARNING(msg)),
            )
        except ValueError as exc:
            raise CommandError(str(exc)) from exc

        action = 'would update' if dry_run else 'updated'
        summary = ', '.join(f'{k}={v}' for k, v in results.items())
        self.stdout.write(self.style.SUCCESS(f'{action}: {summary}'))
