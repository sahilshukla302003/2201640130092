import json
from django.http import JsonResponse, HttpResponseRedirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta
from .models import ShortURL, ClickEvent
from .utils import generateShortcode
from logging_middleware.logger import Log


@csrf_exempt
def createshorturl(request):
    if request.method != "POST":
        Log("backend", "warn", "route", "Invalid method used for createshorturl")
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body.decode())
        long_url = data.get("url")
        validity = int(data.get("validity", 30))
        shortcode = data.get("shortcode") or generateShortcode()

        if not long_url:
            Log("backend", "error", "handler", "Missing URL in request body")
            return JsonResponse({"error": "Missing url"}, status=400)

        if ShortURL.objects.filter(shortcode=shortcode).exists():
            Log("backend", "error", "db", f"Shortcode collision: {shortcode}")
            return JsonResponse({"error": "Shortcode already in use"}, status=409)

        expiry_time = timezone.now() + timedelta(minutes=validity)

        ShortURL.objects.create(
            shortcode=shortcode,
            long_url=long_url,
            expires_at=expiry_time,
        )

        Log("backend", "info", "controller", f"Short URL created: {shortcode}")

        return JsonResponse({
            "shortLink": f"http://{request.get_host()}/{shortcode}",
            "expiry": expiry_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }, status=201)

    except Exception as e:
        Log("backend", "fatal", "service", f"Unexpected error: {str(e)}")
        return JsonResponse({"error": str(e)}, status=400)


def redirectshorturl(request, code):
    try:
        obj = ShortURL.objects.get(shortcode=code)
    except ShortURL.DoesNotExist:
        Log("backend", "error", "db", f"Shortcode not found: {code}")
        return JsonResponse({"error": "Not found"}, status=404)

    if obj.is_expired():
        Log("backend", "warn", "handler", f"Expired shortcode accessed: {code}")
        return JsonResponse({"error": "Expired"}, status=410)

    obj.clicks += 1
    obj.save()
    referrer = request.META.get("HTTP_REFERER", "direct")
    location = request.META.get("REMOTE_ADDR", "unknown")
    ClickEvent.objects.create(short_url=obj, referrer=referrer, location=location)

    Log("backend", "info", "service", f"Redirected {code} to {obj.long_url}")
    return HttpResponseRedirect(obj.long_url)


def shorturlget(request, code):
    try:
        obj = ShortURL.objects.get(shortcode=code)
    except ShortURL.DoesNotExist:
        Log("backend", "error", "db", f"Shortcode not found in stats: {code}")
        return JsonResponse({"error": "Not found"}, status=404)

    clicks = obj.clicks_data.all().values("timestamp", "referrer", "location")

    Log("backend", "info", "controller", f"Stats fetched for shortcode {code}")

    return JsonResponse({
        "shortLink": f"http://{request.get_host()}/{obj.shortcode}",
        "originalURL": obj.long_url,
        "click_details": list(clicks),
        "created_at": obj.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "expiry": obj.expires_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_clicks": obj.clicks,
    }, status=200)
