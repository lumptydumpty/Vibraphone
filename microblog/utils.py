import re
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model

def parse_mentions(text):
    # First, escape the text to prevent XSS
    text = escape(text)

    User = get_user_model()
    # Find all @username patterns. Django usernames can contain letters, numbers, and @/./+/-/_
    # We use a pattern that matches @ followed by valid username characters
    mentions = re.findall(r'@([\w.@+-]+)', text)

    # Sort mentions by length descending to avoid partial replacement of long usernames
    for username in sorted(set(mentions), key=len, reverse=True):
        try:
            # Note: We must be careful about punctuation at the end of the username
            # This is a simplified version; real-world parsing might be more complex
            user = User.objects.get(username=username)
            profile_url = reverse('profile_view_user', kwargs={'username': username})
            mention_link = f'<a href="{profile_url}">@{username}</a>'
            # Use negative lookbehind/lookahead to ensure we match whole usernames
            text = re.sub(fr'@({re.escape(username)})\b', mention_link, text)
        except User.DoesNotExist:
            continue

    return mark_safe(text)
