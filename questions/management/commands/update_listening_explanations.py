"""Backward-compatible wrapper around update_explanations --category listening. """

from django.core.management.base import BaseCommand

from questions.explanation_sync import sync_explanations
from questions.level_paths import add_default_register_arguments


class Command(BaseCommand):
    help = (
        'リスニング解説だけ更新（進捗保持）。'
        '推奨: python manage.py update_explanations --category listening'
    )

    def add_arguments(self, parser):
        add_default_register_arguments(parser)
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='DBを更新せず件数だけ表示',
        )

    def handle(self, *args, **options):
        level = options['level']
        dry_run = options['dry_run']
        results = sync_explanations(
            level=level,
            category='listening',
            dry_run=dry_run,
            log=self.stdout.write,
            warn=lambda msg: self.stdout.write(self.style.WARNING(msg)),
        )
        action = 'would update' if dry_run else 'updated'
        summary = ', '.join(f'{k}={v}' for k, v in results.items())
        self.stdout.write(self.style.SUCCESS(f'{action}: {summary}'))
