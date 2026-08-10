import re

from django.conf import settings


def _build_whatsapp_url(number: str) -> str:
    digits = re.sub(r"\D", "", number or "")
    if digits.startswith("0"):
        digits = "92" + digits[1:]
    return f"https://wa.me/{digits}" if digits else "https://wa.me/"


def site_contact(request):
    number = getattr(settings, "WHATSAPP_NUMBER", "03069789224")
    configured_url = getattr(settings, "WHATSAPP_URL", "")
    return {
        "whatsapp_number": number,
        "whatsapp_url": configured_url or _build_whatsapp_url(number),
    }
