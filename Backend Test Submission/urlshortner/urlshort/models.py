from django.db import models
from django.utils import timezone

class ShortURL(models.Model):
    shortcode = models.SlugField(unique=True, max_length=20)
    long_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    clicks = models.PositiveIntegerField(default=0)


    def is_expired(self):
        return timezone.now() > self.expires_at


class ClickEvent(models.Model):
    short_url = models.ForeignKey(ShortURL, on_delete=models.CASCADE, related_name="clicks_data")
    timestamp = models.DateTimeField(auto_now_add=True)
    referrer = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True) 