from .models import Category, SyriacWord
from django.core.cache import cache
import random

def categories_processor(request):
    """Make categories available to all templates"""
    return {
        'categories': Category.objects.all()
    }

def syriac_word_processor(request):
    """Make daily Syriac word available to all templates"""
    # Try to get from cache first (24-hour cache)
    word_of_day = cache.get('syriac_word_of_day')
    
    # If not in cache, get a random word and cache it
    if not word_of_day:
        words = list(SyriacWord.objects.all())
        if words:
            word_of_day = random.choice(words)
            # Cache for 24 hours (86400 seconds)
            cache.set('syriac_word_of_day', word_of_day, 86400)
        else:
            word_of_day = None
    
    return {
        'syriac_word_of_day': word_of_day,
    }
