import random, string
from .models import ShortURL

def generateShortcode(length=6):
    chars = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choice(chars) for _ in range(length))
        if not ShortURL.objects.filter(shortcode=code).exists():
            return code
