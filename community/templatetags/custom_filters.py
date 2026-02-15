from django import template
from django.utils.html import format_html
import markdown
import re

register = template.Library()

@register.filter
def markdown_to_html(text):
    """Convert markdown to HTML"""
    return markdown.markdown(text, extensions=['extra', 'codehilite'])

@register.filter
def truncate_words(text, words):
    """Truncate text to specified number of words"""
    words_list = text.split()
    if len(words_list) > words:
        return ' '.join(words_list[:words]) + '...'
    return text

@register.filter
def highlight_search(text, query):
    """Highlight search terms in text"""
    if not query:
        return text
    
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return format_html(
        pattern.sub(
            lambda m: f'<span class="bg-warning">{m.group()}</span>',
            str(text)
        )
    )

@register.simple_tag
def get_reading_time(text):
    """Calculate reading time in minutes"""
    words_per_minute = 200
    word_count = len(text.split())
    minutes = round(word_count / words_per_minute)
    
    if minutes < 1:
        return "Less than 1 min read"
    elif minutes == 1:
        return "1 min read"
    else:
        return f"{minutes} min read"

@register.filter
def initials(name):
    """Get initials from name"""
    words = name.split()
    if len(words) >= 2:
        return f"{words[0][0]}{words[1][0]}".upper()
    elif len(words) == 1:
        return words[0][:2].upper()
    return "?"

@register.filter
def youtube_embed(url):
    """Convert YouTube URL to embed URL"""
    youtube_regex = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=)?(.+)'
    match = re.match(youtube_regex, url)
    if match:
        video_id = match.group(1)
        return f"https://www.youtube.com/embed/{video_id}"
    return url

@register.filter
def has_group(user, group_name):
    """Check if user belongs to a group"""
    return user.groups.filter(name=group_name).exists()

@register.simple_tag
def define(val=None):
    """Define a variable in template"""
    return val
