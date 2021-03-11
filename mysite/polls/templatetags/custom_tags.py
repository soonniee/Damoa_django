from django import template
register = template.Library()
from datetime import tzinfo,timedelta,datetime
from pytz import timezone
@register.filter            # 1
def sub(left, right):
    return left - right
@register.simple_tag
def realtime():
    now = datetime.now(timezone('UTC'))
    return now.astimezone(timezone('Asia/Seoul'))
