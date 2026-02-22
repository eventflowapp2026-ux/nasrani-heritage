# community/management/commands/rotate_syriac_word.py
from django.core.management.base import BaseCommand
from community.models import SyriacWord
from django.core.cache import cache
import random

class Command(BaseCommand):
    help = 'Rotate the daily Syriac word'

    def handle(self, *args, **options):
        # Get all words
        words = list(SyriacWord.objects.all())
        
        if not words:
            self.stdout.write(self.style.WARNING('No Syriac words found'))
            return
        
        # Select a random word
        word_of_day = random.choice(words)
        
        # Store in cache with 24-hour timeout (86400 seconds)
        cache.set('syriac_word_of_day', word_of_day, 86400)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully set word of the day: {word_of_day.word}')
        )
