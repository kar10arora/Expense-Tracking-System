# Tracker/apps.py
from django.apps import AppConfig

class TrackerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Tracker'

    def ready(self):
        pass
        # Don't import signals during migration setup
        # import Tracker.signals