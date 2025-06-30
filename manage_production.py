#!/usr/bin/env python
"""
Management script for production environment.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eiken_project.settings_production")
    django.setup()
    execute_from_command_line(sys.argv) 