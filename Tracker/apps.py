# Tracker/apps.py
from django.apps import AppConfig

class TrackerConfig(AppConfig):
    name = 'Tracker'

    def ready(self):
        import Tracker.signals