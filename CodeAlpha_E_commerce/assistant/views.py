from __future__ import annotations

import json

from django.contrib import messages
from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from assistant.forms import AISettingsForm
from assistant.models import AIConversation, AIMessage, AISettings
from assistant.services import build_conversation, conversation_payload, get_or_create_wishlist, process_assistant_message
from core.shopping_auth import redirect_guest_to_login, shopping_action_login_required
from products.models import Product


def _parse_json_body(request) -> dict:
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return {}


def _owned_conversation(request, conversation_id=None):
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    if conversation_id:
        queryset = AIConversation.objects.filter(id=conversation_id, session_key=session_key)
        if request.user.is_authenticated:
            conversation = queryset.filter(user=request.user).first() or AIConversation.objects.filter(
                id=conversation_id,
                session_key=session_key,
                user__isnull=True,
            ).first()
        else:
            conversation = queryset.filter(user__isnull=True).first()
        if conversation:
            return conversation
    return build_conversation(request)


@require_http_methods(["GET"])
def state_api(request):
    conversation_id = request.GET.get("conversation_id")
    try:
        conversation_pk = int(conversation_id) if conversation_id else None
    except (TypeError, ValueError):
        conversation_pk = None
    conversation = _owned_conversation(request, conversation_id=conversation_pk)
    settings_obj = AISettings.load()
    payload = conversation_payload(conversation, limit=40)
    payload.update(
        {
            "enabled": settings_obj.enabled,
            "assistant_name": settings_obj.assistant_name,
            "welcome_message": settings_obj.welcome_message,
            "voice_enabled": settings_obj.voice_enabled,
            "supported_languages": settings_obj.supported_languages,
            "conversation_id": conversation.id,
        }
    )
    return JsonResponse(payload)


@require_http_methods(["GET", "POST"])
def chat_api(request):
    settings_obj = AISettings.load()
    if request.method == "GET":
        return state_api(request)

    payload = _parse_json_body(request)
    conversation_id = payload.get("conversation_id")
    try:
        conversation_pk = int(conversation_id) if conversation_id else None
    except (TypeError, ValueError):
        conversation_pk = None
    conversation = _owned_conversation(request, conversation_id=conversation_pk)
    action = (payload.get("action") or "").strip().lower()

    if action == "clear":
        with transaction.atomic():
            conversation.messages.all().delete()
            conversation.memory = {}
            conversation.language = "en"
            conversation.title = "Shopping Assistant"
            conversation.save(update_fields=["memory", "language", "title"])
            AIMessage.objects.create(
                conversation=conversation,
                sender=AIMessage.SENDER_ASSISTANT,
                content=settings_obj.welcome_message,
                language="en",
                status="delivered",
                metadata={"intent": "welcome"},
            )
        return JsonResponse(
            {
                "ok": True,
                "conversation_id": conversation.id,
                "assistant": {
                    "content": settings_obj.welcome_message,
                    "language": "en",
                    "intent": "welcome",
                    "actions": [],
                    "products": [],
                },
                "conversation": conversation_payload(conversation, limit=40),
            }
        )

    message = (payload.get("message") or "").strip()
    if not message:
        return JsonResponse({"ok": False, "error": "Message is required."}, status=400)

    reply = process_assistant_message(request, conversation, message, is_voice=bool(payload.get("is_voice")))
    return JsonResponse(
        {
            "ok": True,
            "conversation_id": conversation.id,
            "assistant": {
                "content": reply.text,
                "voice_text": reply.voice_text,
                "language": reply.language,
                "intent": reply.intent,
                "actions": reply.actions,
                "products": reply.products,
                "metadata": reply.metadata,
            },
            "login_required": bool(reply.metadata.get("login_required")),
            "login_url": reply.metadata.get("login_url", ""),
            "register_url": reply.metadata.get("register_url", ""),
            "conversation": conversation_payload(conversation, limit=40),
        }
    )


@shopping_action_login_required("Please sign in to save and view your wishlist.")
@require_http_methods(["GET"])
def wishlist_page(request):
    wishlist = get_or_create_wishlist(request)
    if wishlist is None:
        return redirect_guest_to_login(
            request,
            "Please sign in to save and view your wishlist.",
            action_type="wishlist",
            next_url=request.get_full_path(),
        )
    items = wishlist.items.select_related("product", "product__brand", "product__category").order_by("-added_at")
    return render(request, "assistant/wishlist.html", {"wishlist": wishlist, "items": items})


@require_http_methods(["POST"])
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    if not request.user.is_authenticated:
        return redirect_guest_to_login(
            request,
            "Please sign in to save and view your wishlist.",
            action_type="wishlist",
            product_id=product.id,
            next_url=request.META.get("HTTP_REFERER") or product.get_absolute_url(),
        )
    wishlist = get_or_create_wishlist(request)
    item = wishlist.items.filter(product=product).first()
    if item:
        item.delete()
        messages.success(request, f"{product.name} removed from wishlist.")
    else:
        wishlist.items.create(product=product)
        messages.success(request, f"{product.name} added to wishlist.")
    return redirect(request.META.get("HTTP_REFERER") or reverse("assistant:wishlist"))
