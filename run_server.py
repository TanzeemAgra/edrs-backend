#!/usr/bin/env python
"""
Simple Django server start script
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    
    from django.core.management import execute_from_command_line
    
    # Start the development server
    sys.argv = ['manage.py', 'runserver', '0.0.0.0:8000', '--noreload', '--insecure']
    execute_from_command_line(sys.argv)