# P&ID Analysis App for EDRS
# Advanced Oil & Gas Process Diagram Analysis

from django.apps import AppConfig


class PidAnalysisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.pid_analysis'
    verbose_name = 'P&ID Analysis & Error Detection'

    def ready(self):
        """Initialize P&ID analysis components"""
        pass