"""
Django command to wait for the data base to be avilable
"""

from django.core.management import BaseCommand


class Command(BaseCommand):
    """Django command to wait for data base"""

    def handle(self,*args, **options):
        pass