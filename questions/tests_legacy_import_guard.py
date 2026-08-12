from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, TestCase, override_settings


class LegacyImportGuardTest(TestCase):
    def test_register_grammar_blocked_by_default(self):
        with self.assertRaises(CommandError) as ctx:
            call_command('register_grammar_fill_questions', level='5')
        self.assertIn('配信パイプラインから切り離されています', str(ctx.exception))


class LegacyPdfGuardTest(SimpleTestCase):
    def test_pdf_tool_exits_without_env(self):
        import os
        import subprocess
        import sys
        from pathlib import Path

        env = os.environ.copy()
        env.pop('ALLOW_LEGACY_PDF_IMPORT', None)
        script = Path(__file__).resolve().parents[1] / 'utils' / 'build_level5_questions.py'
        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            env=env,
            cwd=str(script.parents[1]),
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn('配信から切り離されています', result.stderr)
