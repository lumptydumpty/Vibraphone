from django import template
from ..utils import parse_mentions

register = template.Library()

@register.filter(name='parse_mentions_tag')
def parse_mentions_tag(text):
    return parse_mentions(text)
