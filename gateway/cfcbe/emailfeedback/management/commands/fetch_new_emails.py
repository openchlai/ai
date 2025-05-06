from django.core.management.base import BaseCommand
from emailfeedback.utils import fetch_emails

class Command(BaseCommand):
    help = 'Fetch emails and store them in the database'

    def handle(self, *args, **kwargs):
        fetch_emails('frankline.karanja@bitz-itc.com', 'KnurfFrank!!')
        self.stdout.write(self.style.SUCCESS('Emails fetched successfully'))
