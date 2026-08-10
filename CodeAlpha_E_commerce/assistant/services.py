from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Iterable
from urllib.parse import quote

from django.conf import settings
from django.db.models import Avg, Count
from django.urls import reverse

from assistant.models import AIConversation, AIMessage, AISettings, AIVoiceLog, Wishlist, WishlistItem
from cart.models import CartItem
from cart.services import get_or_create_cart
from core.shopping_auth import auth_required_json_payload, store_pending_shopping_action
from orders.models import Order
from products.models import Brand, Category, Product


URDU_RE = re.compile(r"[\u0600-\u06FF]")
ROMAN_URDU_HINTS = {
    "assalam",
    "salam",
    "kya",
    "mujhe",
    "acha",
    "accha",
    "batao",
    "sir",
    "bhai",
    "mera",
    "budget",
    "recommend",
    "sasta",
    "mehnga",
}

STOPWORDS = {
    "show",
    "me",
    "the",
    "a",
    "an",
    "best",
    "latest",
    "cheap",
    "good",
    "nice",
    "for",
    "under",
    "less",
    "than",
    "please",
    "suggest",
    "recommend",
    "i",
    "need",
    "want",
    "to",
    "buy",
    "find",
    "compare",
    "price",
    "prices",
}


@dataclass
class AssistantReply:
    text: str
    voice_text: str
    language: str
    intent: str
    products: list[dict[str, Any]]
    actions: list[dict[str, Any]]
    metadata: dict[str, Any]


def get_ai_settings() -> AISettings:
    return AISettings.load()


def detect_language(text: str) -> str:
    normalized = (text or "").strip().lower()
    if not normalized:
        return "en"
    if URDU_RE.search(normalized):
        if any(token in normalized for token in ("اور", "لیکن", "best", "price", "camera")):
            return "mixed"
        return "ur"
    tokens = set(re.findall(r"[a-z]+", normalized))
    if tokens & ROMAN_URDU_HINTS:
        if len(tokens & {"show", "best", "camera", "phone", "laptop", "gaming", "budget"}) >= 2:
            return "mixed"
        return "roman_ur"
    return "en"


def _language_voice_code(language: str) -> str:
    return "ur-PK" if language == "ur" else "en-US"


def _money(value: Decimal | int | float | None) -> str:
    if value is None:
        value = 0
    price_val = Decimal(str(value))
    
    try:
        from core.middleware import current_request
        request = current_request.get()
    except Exception:
        request = None
        
    if request and hasattr(request, 'localization'):
        loc = request.localization
        rate = Decimal(loc['rate'])
        symbol = loc['symbol']
        converted = price_val * rate
        if converted % 1 == 0:
            return f"{symbol}{int(converted):,}"
        return f"{symbol}{converted:,.2f}"
        
    return f"PKR {int(price_val):,}"


def extract_budget(text: str) -> Decimal | None:
    text = (text or "").lower().replace(",", "")
    patterns = [
        r"(\d+(?:\.\d+)?)\s*(k|thousand)",
        r"(\d+(?:\.\d+)?)\s*(lakh|lac)",
        r"(\d+(?:\.\d+)?)\s*(m|million)",
        r"under\s*(\d+)",
        r"below\s*(\d+)",
        r"less than\s*(\d+)",
        r"budget\s*(\d+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            amount = Decimal(match.group(1))
            suffix = match.group(2) if len(match.groups()) > 1 else None
            if suffix in {"k", "thousand"}:
                amount *= 1000
            elif suffix in {"lakh", "lac"}:
                amount *= 100000
            elif suffix in {"m", "million"}:
                amount *= 1000000
            return amount
    direct = re.search(r"\b(\d{4,7})\b", text)
    if direct:
        return Decimal(direct.group(1))
    return None


def _tokenize(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-z0-9]+", (text or "").lower()) if token not in STOPWORDS]


def _product_search_space(product: Product) -> str:
    spec_text = " ".join(f"{k} {v}" for k, v in (product.specs or {}).items())
    return " ".join(
        [
            product.name,
            product.short_description,
            product.description,
            product.brand.name,
            product.category.name,
            spec_text,
        ]
    ).lower()


def _product_score(product: Product, query: str, budget: Decimal | None = None, preference: str | None = None) -> float:
    score = float(product.rating or 0) * 2
    searchable = _product_search_space(product)
    tokens = _tokenize(query)
    for token in tokens:
        if token in searchable:
            score += 4
    if budget is not None:
        if product.price <= budget:
            score += 8
            score += max(0, float(budget - product.price) / 10000)
        else:
            score -= float(product.price - budget) / 10000
    if preference and preference.lower() in searchable:
        score += 6
    if product.is_featured:
        score += 2
    if product.compare_at_price and product.compare_at_price > product.price:
        score += 1
    if product.stock <= 0:
        score -= 12
    return score


def search_products(
    query: str,
    *,
    budget: Decimal | None = None,
    brand_name: str | None = None,
    category_name: str | None = None,
    limit: int = 6,
) -> list[Product]:
    products = list(
        Product.objects.filter(is_active=True)
        .select_related("brand", "category")
        .prefetch_related("images", "variants", "reviews")
    )
    ranked = []
    tokens = _tokenize(query)
    
    for product in products:
        score = _product_score(product, query, budget=budget, preference=brand_name or category_name)
        if brand_name and brand_name.lower() not in _product_search_space(product):
            score -= 2
        if category_name and category_name.lower() not in _product_search_space(product):
            score -= 2
            
        matches_token = any(t in _product_search_space(product) for t in tokens)
        if not budget and not brand_name and not category_name and tokens and not matches_token:
            score = -999
            
        ranked.append((score, product))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [product for score, product in ranked[:limit] if score > 0]


def _product_to_dict(product: Product) -> dict[str, Any]:
    return {
        "id": product.id,
        "name": product.name,
        "slug": product.slug,
        "brand": product.brand.name,
        "category": product.category.name,
        "price": float(product.price),
        "price_label": _money(product.price),
        "compare_at_price": float(product.compare_at_price) if product.compare_at_price else None,
        "compare_label": _money(product.compare_at_price) if product.compare_at_price else "",
        "rating": float(product.rating),
        "stock": product.stock,
        "short_description": product.short_description,
        "image": product.primary_image,
        "url": product.get_absolute_url(),
        "on_sale": bool(product.on_sale),
        "specs": product.specs or {},
    }


def _category_from_text(text: str) -> Category | None:
    text = (text or "").lower()
    if any(k in text for k in ("laptop", "macbook", "notebook", "chromebook")):
        return Category.objects.filter(slug__in=["laptops", "laptop"]).first()
    if any(k in text for k in ("phone", "mobile", "smartphone", "iphone", "galaxy")):
        return Category.objects.filter(slug__in=["smartphones", "smartphone", "phones"]).first()
    if any(k in text for k in ("gaming", "console", "playstation", "xbox")):
        return Category.objects.filter(slug="gaming").first()
    if any(k in text for k in ("display", "monitor", "screen")):
        return Category.objects.filter(slug="displays").first()
    if any(k in text for k in ("audio", "headphone", "earbud", "airpods")):
        return Category.objects.filter(slug="audio").first()
    if any(k in text for k in ("accessor", "charger", "keyboard", "mouse")):
        return Category.objects.filter(slug="accessories").first()
    return None


def _brand_from_text(text: str) -> Brand | None:
    text = (text or "").lower()
    if any(k in text for k in ("apple", "iphone", "ipad", "macbook", "airpods")):
        b = Brand.objects.filter(name__iexact="Apple").first() or Brand.objects.filter(name__icontains="Apple").first()
        if b: return b
    if any(k in text for k in ("samsung", "galaxy")):
        b = Brand.objects.filter(name__iexact="Samsung").first() or Brand.objects.filter(name__icontains="Samsung").first()
        if b: return b
    if any(k in text for k in ("dell", "xps")):
        b = Brand.objects.filter(name__iexact="Dell").first() or Brand.objects.filter(name__icontains="Dell").first()
        if b: return b
    if any(k in text for k in ("hp", "spectre", "pavilion")):
        b = Brand.objects.filter(name__iexact="HP").first() or Brand.objects.filter(name__icontains="HP").first()
        if b: return b
    if any(k in text for k in ("lenovo", "thinkpad")):
        b = Brand.objects.filter(name__iexact="Lenovo").first() or Brand.objects.filter(name__icontains="Lenovo").first()
        if b: return b
    if any(k in text for k in ("asus", "rog")):
        b = Brand.objects.filter(name__iexact="Asus").first() or Brand.objects.filter(name__icontains="Asus").first()
        if b: return b
    if any(k in text for k in ("sony", "playstation")):
        b = Brand.objects.filter(name__iexact="Sony").first() or Brand.objects.filter(name__icontains="Sony").first()
        if b: return b
    for brand in Brand.objects.all():
        if brand.name.lower() in text:
            return brand
    return None


def _format_product_line(product: Product, language: str) -> str:
    base = f"{product.name} - {_money(product.price)}"
    if language in {"ur", "roman_ur", "mixed"}:
        if product.on_sale:
            return f"{product.name} - {_money(product.price)}. Sale par hai."
        return base
    if product.on_sale:
        return f"{base} (was {_money(product.compare_at_price)})"
    return base


def _greeting(language: str) -> str:
    if language == "ur":
        return (
            "السلام علیکم! CA-Tech Electronics AI اسسٹنٹ میں خوش آمدید۔\n\n"
            "میں آپ کی مصنوعات ڈھونڈنے، آرڈرز چیک کرنے اور بہترین ڈیلز منتخب کرنے میں کیا مدد کر سکتا ہوں؟"
        )
    if language in {"roman_ur", "mixed"}:
        return (
            "Assalam-o-Alaikum! CA-Tech AI Assistant mein khushamdeed.\n\n"
            "Main aap ki best products dhoondne, prices compare karne aur orders check karne mein madad kar sakta hoon. Aaj kya dekhna chahenge?"
        )
    return (
        "Hello! Welcome to CA-Tech Electronics.\n\n"
        "I'm your AI Shopping Assistant. How can I help you find the perfect tech or assist with your orders today?"
    )


def _authenticated_greeting(request, language: str) -> str:
    user = request.user
    display_name = user.get_full_name() or user.first_name or user.username
    cart = get_or_create_cart(request)
    cart_count = cart.item_count if cart else 0
    pending_orders = 0
    if user.is_authenticated:
        pending_orders = user.orders.exclude(status__in={Order.COMPLETED, Order.CANCELLED}).count()
    if language == "ur":
        return (
            f"خوش آمدید {display_name}!\n\n"
            f"آپ کے کارٹ میں اس وقت {cart_count} پروڈکٹس ہیں اور {pending_orders} آرڈرز زیرِ عمل ہیں۔\n"
            "میں آپ کی مزید کیا مدد کر سکتا ہوں؟"
        )
    if language in {"roman_ur", "mixed"}:
        return (
            f"Welcome back, {display_name}!\n\n"
            f"Aap ke cart mein is waqt {cart_count} items hain aur {pending_orders} active orders hain.\n"
            "Aaj aap kya search ya compare karna chahenge?"
        )
    return (
        f"Welcome back, {display_name}!\n\n"
        f"You currently have {cart_count} item{'s' if cart_count != 1 else ''} in your cart and {pending_orders} active order{'s' if pending_orders != 1 else ''}.\n"
        "How can I assist you with your shopping today?"
    )


def _extract_entities(text: str) -> dict[str, Any]:
    return {
        "budget": extract_budget(text),
        "brand": _brand_from_text(text),
        "category": _category_from_text(text),
    }


def _update_memory(conversation: AIConversation, text: str, entities: dict[str, Any], product_ids: list[int] | None = None) -> None:
    memory = dict(conversation.memory or {})
    if entities.get("budget") is not None:
        memory["budget"] = str(entities["budget"])
    if entities.get("brand"):
        memory["brand"] = entities["brand"].name
    elif entities.get("category"):
        memory.pop("brand", None)
    if entities.get("category"):
        memory["category"] = entities["category"].name
    elif entities.get("brand"):
        memory.pop("category", None)
    if product_ids:
        memory["last_product_ids"] = product_ids
    memory["last_query"] = text
    conversation.memory = memory
    conversation.language = conversation.language or detect_language(text)
    conversation.save(update_fields=["memory", "language", "last_message_at"])


def _last_products_from_memory(conversation: AIConversation) -> list[Product]:
    memory = conversation.memory or {}
    ids = memory.get("last_product_ids") or []
    products = list(Product.objects.filter(id__in=ids).select_related("brand", "category").prefetch_related("images", "variants"))
    if products:
        return products
    return list(
        Product.objects.filter(is_active=True)
        .select_related("brand", "category")
        .prefetch_related("images", "variants")
        .order_by("-created_at")[:2]
    )


def _comparison_block(products: list[Product], language: str) -> str:
    if len(products) < 2:
        return ""
    left, right = products[:2]
    left_specs = left.specs or {}
    right_specs = right.specs or {}
    if language == "ur":
        return (
            f"{left.name} aur {right.name} ka mukhtasar comparison:\n"
            f"Price: { _money(left.price) } vs { _money(right.price) }\n"
            f"Display: {left_specs.get('Display', left_specs.get('Screen', 'N/A'))} vs {right_specs.get('Display', right_specs.get('Screen', 'N/A'))}\n"
            f"RAM: {left_specs.get('Memory', left_specs.get('RAM', 'N/A'))} vs {right_specs.get('Memory', right_specs.get('RAM', 'N/A'))}\n"
            f"Battery: {left_specs.get('Battery', 'N/A')} vs {right_specs.get('Battery', 'N/A')}\n"
            f"Recommendation: {left.name if left.rating >= right.rating else right.name}"
        )
    if language in {"roman_ur", "mixed"}:
        return (
            f"{left.name} aur {right.name} ka comparison:\n"
            f"Price: {_money(left.price)} vs {_money(right.price)}\n"
            f"Display: {left_specs.get('Display', left_specs.get('Screen', 'N/A'))} vs {right_specs.get('Display', right_specs.get('Screen', 'N/A'))}\n"
            f"RAM: {left_specs.get('Memory', left_specs.get('RAM', 'N/A'))} vs {right_specs.get('Memory', right_specs.get('RAM', 'N/A'))}\n"
            f"Battery: {left_specs.get('Battery', 'N/A')} vs {right_specs.get('Battery', 'N/A')}\n"
            f"Recommendation: {left.name if left.rating >= right.rating else right.name}"
        )
    return (
        f"Comparison between {left.name} and {right.name}:\n"
        f"Price: {_money(left.price)} vs {_money(right.price)}\n"
        f"Display: {left_specs.get('Display', left_specs.get('Screen', 'N/A'))} vs {right_specs.get('Display', right_specs.get('Screen', 'N/A'))}\n"
        f"RAM: {left_specs.get('Memory', left_specs.get('RAM', 'N/A'))} vs {right_specs.get('Memory', right_specs.get('RAM', 'N/A'))}\n"
        f"Battery: {left_specs.get('Battery', 'N/A')} vs {right_specs.get('Battery', 'N/A')}\n"
        f"Recommendation: {left.name if left.rating >= right.rating else right.name}"
    )


def _product_insight(product: Product, language: str) -> str:
    specs = product.specs or {}
    camera = specs.get("Camera", "Not specified")
    battery = specs.get("Battery", "Not specified")
    processor = specs.get("CPU", specs.get("Processor", "Not specified"))
    ram = specs.get("Memory", specs.get("RAM", "Not specified"))
    storage = specs.get("Storage", "Not specified")
    display = specs.get("Display", specs.get("Screen", "Not specified"))
    if language == "ur":
        return (
            f"{product.name} ke bare mein:\n"
            f"Camera: {camera}\nDisplay: {display}\nBattery: {battery}\nProcessor: {processor}\nRAM: {ram}\nStorage: {storage}"
        )
    if language in {"roman_ur", "mixed"}:
        return (
            f"{product.name} ke bare mein:\n"
            f"Camera: {camera}\nDisplay: {display}\nBattery: {battery}\nProcessor: {processor}\nRAM: {ram}\nStorage: {storage}"
        )
    return (
        f"{product.name} details:\n"
        f"Camera: {camera}\nDisplay: {display}\nBattery: {battery}\nProcessor: {processor}\nRAM: {ram}\nStorage: {storage}"
    )


def _recommendation_reason(product: Product, use_case: str | None, budget: Decimal | None) -> str:
    reasons = []
    if product.on_sale:
        reasons.append("on sale")
    if budget and product.price <= budget:
        reasons.append("fits your budget")
    if use_case:
        reasons.append(f"suited for {use_case}")
    if product.stock > 10:
        reasons.append("good stock availability")
    if not reasons:
        reasons.append("strong overall value")
    return ", ".join(reasons)


def _detect_use_case(text: str) -> str | None:
    text = (text or "").lower()
    for key in ("gaming", "programming", "office", "photography", "video editing", "business", "travel", "student"):
        if key in text:
            return key
    return None


def _intent_from_text(text: str) -> str:
    lowered = (text or "").lower()
    if any(word in lowered for word in ("compare", "vs", "versus")):
        return "compare"
    if any(word in lowered for word in ("add", "cart")):
        return "add_to_cart"
    if any(word in lowered for word in ("remove", "delete")) and "cart" in lowered:
        return "remove_from_cart"
    if any(word in lowered for word in ("wishlist", "save")):
        return "wishlist"
    if any(word in lowered for word in ("checkout", "proceed to checkout", "buy now", "buy", "purchase", "place order", "place my order", "complete order")):
        return "checkout"
    if "track" in lowered or "order history" in lowered or "my orders" in lowered or "tracking" in lowered:
        return "orders"
    if any(word in lowered for word in ("dashboard", "profile", "account", "home", "store")):
        return "navigation"
    if any(word in lowered for word in ("show", "find", "recommend", "suggest", "latest", "sale", "under", "budget", "best")):
        return "search"
    if lowered.strip() in {"hello", "hi", "salam", "assalam o alaikum", "assalamualaikum", "assalam o alaikum."}:
        return "greeting"
    return "general"


def _current_user_order_context(user) -> str | None:
    if not user or not user.is_authenticated:
        return None
    order = user.orders.prefetch_related("items").first()
    if not order:
        return None
    return f"{order.order_number} / {order.get_payment_status_display()} / {order.get_status_display()}"


def _make_navigation_action(action: str, label: str, url: str) -> dict[str, Any]:
    return {"type": action, "label": label, "url": url}


def _auth_prompt_reply(request, language: str, text: str, *, action_type: str, next_url: str, **payload) -> AssistantReply:
    store_pending_shopping_action(request, action_type, next_url=next_url, **payload)
    login_url = reverse("accounts:login")
    register_url = reverse("accounts:register")
    actions = [
        _make_navigation_action("navigate", "Login", f"{login_url}?next={quote(next_url)}"),
        _make_navigation_action("navigate", "Create Account", f"{register_url}?next={quote(next_url)}"),
    ]
    return AssistantReply(
        text=text,
        voice_text=text,
        language=language,
        intent=action_type,
        products=[],
        actions=actions,
        metadata={
            "login_required": True,
            "login_url": f"{login_url}?next={quote(next_url)}",
            "register_url": f"{register_url}?next={quote(next_url)}",
            "pending_action": action_type,
            **payload,
        },
    )


def _product_actions(products: list[Product]) -> list[dict[str, Any]]:
    return [
        {
            "type": "product",
            "id": product.id,
            "name": product.name,
            "price": _money(product.price),
            "image": product.primary_image,
            "url": product.get_absolute_url(),
            "brand": product.brand.name,
            "category": product.category.name,
        }
        for product in products
    ]


def _resolve_products_from_text(text: str, conversation: AIConversation) -> list[Product]:
    entities = _extract_entities(text)
    brand_name = entities["brand"].name if entities.get("brand") else None
    category_name = entities["category"].name if entities.get("category") else None
    budget = entities["budget"]

    memory = conversation.memory or {}
    if not brand_name and not category_name:
        tokens = _tokenize(text)
        if not tokens or any(t in ("more", "cheap", "cheaper", "expensive", "best", "other", "else", "under", "below") for t in tokens):
            brand_name = memory.get("brand")
            category_name = memory.get("category")

    if budget is None and (not brand_name and not category_name):
        budget = Decimal(memory["budget"]) if memory.get("budget") else None

    return search_products(
        text,
        budget=budget,
        brand_name=brand_name,
        category_name=category_name,
        limit=6,
    )


def _reply_for_search(text: str, conversation: AIConversation, language: str) -> AssistantReply:
    entities = _extract_entities(text)
    budget = entities["budget"]
    memory = conversation.memory or {}
    if budget is None and memory.get("budget"):
        budget = Decimal(memory["budget"])
    brand_name = entities["brand"].name if entities["brand"] else memory.get("brand")
    category_name = entities["category"].name if entities["category"] else memory.get("category")
    use_case = _detect_use_case(text)
    products = search_products(text, budget=budget, brand_name=brand_name, category_name=category_name, limit=6)
    if not products:
        products = list(
            Product.objects.filter(is_active=True)
            .select_related("brand", "category")
            .prefetch_related("images", "variants")
            .order_by("-rating", "-is_featured")[:6]
        )

    if language == "ur":
        intro = "بالکل! میں نے آپ کی تلاش کے مطابق بہترین پروڈکٹس منتخب کی ہیں:"
    elif language in {"roman_ur", "mixed"}:
        intro = "Bilkul! Main ne aap ki query ke mutabiq yeh best products dhoond li hain:"
    else:
        intro = "Here are the top options I recommend for you:"

    lines = [intro, ""]
    if budget:
        lines.append(f"• **Budget**: {_money(budget)}")
    if brand_name:
        lines.append(f"• **Brand**: {brand_name}")
    if category_name:
        lines.append(f"• **Category**: {category_name}")
    if follow_up:
        lines.append(f"• **Note**: {follow_up}")
    lines.append("")
    for idx, product in enumerate(products[:4], start=1):
        lines.append(f"**{idx}.** {_format_product_line(product, language)}")

    metadata = {
        "intent": "search",
        "budget": str(budget) if budget else None,
        "brand": brand_name,
        "category": category_name,
        "use_case": use_case,
        "product_ids": [product.id for product in products[:4]],
    }

    return AssistantReply(
        text="\n".join(lines),
        voice_text=" ".join(lines),
        language=language,
        intent="search",
        products=[_product_to_dict(product) for product in products[:4]],
        actions=[{"type": "show_products", "count": len(products[:4])}],
        metadata=metadata,
    )


def _reply_for_compare(text: str, conversation: AIConversation, language: str) -> AssistantReply:
    products = _resolve_products_from_text(text, conversation)
    if len(products) < 2:
        products = _last_products_from_memory(conversation)
    if len(products) < 2:
        reply = "I need at least two products to compare."
        if language == "ur":
            reply = "Comparison ke liye kam az kam do products chahiye."
        elif language in {"roman_ur", "mixed"}:
            reply = "Comparison ke liye kam az kam do products chahiye."
        return AssistantReply(reply, reply, language, "compare", [], [], {})
    left, right = products[:2]
    comparison = _comparison_block(products[:2], language)
    left_specs = left.specs or {}
    right_specs = right.specs or {}
    left_advantages = []
    right_advantages = []
    left_disadvantages = []
    right_disadvantages = []
    if left.price <= right.price:
        left_advantages.append("better price")
    else:
        right_advantages.append("better price")
    if float(left.rating or 0) >= float(right.rating or 0):
        left_advantages.append("stronger rating")
    else:
        right_advantages.append("stronger rating")
    if left.stock >= right.stock:
        left_advantages.append("better availability")
    else:
        right_advantages.append("better availability")
    if left.price > right.price:
        left_disadvantages.append("higher price")
    if right.price > left.price:
        right_disadvantages.append("higher price")
    if not left_specs.get("Battery"):
        left_disadvantages.append("battery not specified")
    if not right_specs.get("Battery"):
        right_disadvantages.append("battery not specified")
    recommendation = left if float(left.rating or 0) >= float(right.rating or 0) else right
    comparison = "\n".join(
        [
            comparison,
            "",
            f"Advantages: {left.name} - {', '.join(left_advantages) or 'balanced'}; {right.name} - {', '.join(right_advantages) or 'balanced'}",
            f"Disadvantages: {left.name} - {', '.join(left_disadvantages) or 'none major'}; {right.name} - {', '.join(right_disadvantages) or 'none major'}",
            f"Recommendation: {recommendation.name} gives the better overall value for most shoppers.",
        ]
    )
    metadata = {"intent": "compare", "product_ids": [p.id for p in products[:2]]}
    return AssistantReply(
        text=comparison,
        voice_text=comparison,
        language=language,
        intent="compare",
        products=[_product_to_dict(product) for product in products[:2]],
        actions=[],
        metadata=metadata,
    )


def _reply_for_greeting(language: str) -> AssistantReply:
    text = _greeting(language)
    return AssistantReply(text, text, language, "greeting", [], [], {})


def _latest_orders(user, limit: int = 3) -> list[Order]:
    if not user or not user.is_authenticated:
        return []
    return list(user.orders.prefetch_related("items").all()[:limit])


def _reply_for_orders(request, user, language: str) -> AssistantReply:
    if not user or not user.is_authenticated:
        text = "Please log in to your CA-Tech account first. After signing in, I will complete your request."
        if language == "ur":
            text = "Apni order history dekhne ke liye pehle login karein."
        elif language in {"roman_ur", "mixed"}:
            text = "Apni order history dekhne ke liye pehle login karein."
        return _auth_prompt_reply(request, language, text, action_type="orders", next_url=reverse("orders:history"))
    orders = _latest_orders(user)
    if not orders:
        text = "You have no orders yet."
        if language == "ur":
            text = "Abhi tak aap ka koi order nahi hai."
        elif language in {"roman_ur", "mixed"}:
            text = "Abhi tak aap ka koi order nahi hai."
        return AssistantReply(text, text, language, "orders", [], [_make_navigation_action("navigate", "Open Orders", reverse("orders:history"))], {})
    latest = orders[0]
    text = (
        f"Latest order {latest.order_number} is {latest.get_status_display()} and payment is {latest.get_payment_status_display()}."
    )
    if language == "ur":
        text = f"Aap ka latest order {latest.order_number} hai. Status {latest.get_status_display()} hai aur payment {latest.get_payment_status_display()} hai."
    elif language in {"roman_ur", "mixed"}:
        text = f"Aap ka latest order {latest.order_number} hai. Status {latest.get_status_display()} hai aur payment {latest.get_payment_status_display()} hai."
    actions = [_make_navigation_action("navigate", "Open Order History", reverse("orders:history"))]
    return AssistantReply(
        text=text,
        voice_text=text,
        language=language,
        intent="orders",
        products=[],
        actions=actions,
        metadata={
            "orders": [
                {
                    "number": order.order_number,
                    "status": order.status,
                    "payment_status": order.payment_status,
                    "payment_gateway": getattr(order, "payment_gateway", ""),
                    "transaction_id": getattr(order, "transaction_id", ""),
                }
                for order in orders
            ]
        },
    )


def _reply_for_navigation(text: str, language: str) -> AssistantReply:
    lowered = text.lower()
    if "cart" in lowered:
        url = reverse("cart:detail")
        label = "Open Cart"
    elif "checkout" in lowered:
        url = reverse("orders:checkout")
        label = "Proceed to Checkout"
    elif "dashboard" in lowered:
        url = reverse("customer_dashboard")
        label = "Open Dashboard"
    elif "smartphone" in lowered or "phone" in lowered:
        url = reverse("category_page", kwargs={"category_slug": "smartphones"})
        label = "Open Smartphones"
    elif "profile" in lowered or "account" in lowered:
        url = reverse("accounts:profile")
        label = "Open Profile"
    elif "wishlist" in lowered:
        url = reverse("assistant:wishlist")
        label = "Open Wishlist"
    else:
        url = reverse("core:home")
        label = "Open Store"
    if language == "ur":
        text = "Main aap ko relevant page par le ja raha hoon."
    elif language in {"roman_ur", "mixed"}:
        text = "Main aap ko relevant page par le ja raha hoon."
    else:
        text = "I’m opening the relevant page for you."
    return AssistantReply(text, text, language, "navigation", [], [_make_navigation_action("navigate", label, url)], {})


def _guest_shopping_reply(request, text: str, conversation: AIConversation, language: str, intent: str) -> AssistantReply | None:
    lowered = text.lower()
    next_url = request.META.get("HTTP_REFERER") or conversation.source_page or reverse("core:home")
    products = _resolve_products_from_text(text, conversation)
    product = products[0] if products else None

    if "open" in lowered and "cart" in lowered:
        return _auth_prompt_reply(
            request,
            language,
            "Please log in to your CA-Tech account first. After signing in, I will complete your request.",
            action_type="cart",
            next_url=next_url,
        )

    if "wishlist" in lowered or "save" in lowered:
        return _auth_prompt_reply(
            request,
            language,
            "Please log in to your CA-Tech account first. After signing in, I will complete your request.",
            action_type="wishlist",
            next_url=next_url,
            product_id=product.id if product else None,
        )

    if "cart" in lowered or "bag" in lowered or intent == "add_to_cart":
        action_type = "buy_now" if any(word in lowered for word in ("buy now", "buy", "purchase")) else "add_to_cart"
        return _auth_prompt_reply(
            request,
            language,
            "Please log in to your CA-Tech account first. After signing in, I will complete your request.",
            action_type=action_type,
            next_url=next_url,
            product_id=product.id if product else None,
            variant_id=product.variants.first().id if product and product.variants.exists() else None,
            quantity=1,
        )

    if product and any(word in lowered for word in ("buy now", "buy", "purchase")):
        return _auth_prompt_reply(
            request,
            language,
            "Please log in to your CA-Tech account first. After signing in, I will complete your request.",
            action_type="buy_now",
            next_url=next_url,
            product_id=product.id,
            variant_id=product.variants.first().id if product.variants.exists() else None,
            quantity=1,
        )

    if intent == "checkout" or any(word in lowered for word in ("checkout", "place order", "place my order")):
        return _auth_prompt_reply(
            request,
            language,
            "Please log in to your CA-Tech account first. After signing in, I will complete your request.",
            action_type="checkout",
            next_url=next_url,
            product_id=product.id if product else None,
        )

    if intent == "orders":
        return _auth_prompt_reply(
            request,
            language,
            "Please log in to your CA-Tech account first. After signing in, I will complete your request.",
            action_type="orders",
            next_url=next_url,
        )

    if intent == "navigation" and any(word in lowered for word in ("profile", "account", "dashboard")):
        return _auth_prompt_reply(
            request,
            language,
            "Please log in to your CA-Tech account first. After signing in, I will complete your request.",
            action_type="profile",
            next_url=next_url,
        )

    return None


def _reply_for_wishlist(request, text: str, conversation: AIConversation, language: str) -> AssistantReply:
    wishlist = get_or_create_wishlist(request)
    if wishlist is None:
        return _auth_prompt_reply(
            request,
            language,
            "Please log in to your CA-Tech account first. After signing in, I will complete your request.",
            action_type="wishlist",
            next_url=request.META.get("HTTP_REFERER") or conversation.source_page or reverse("core:home"),
        )
    products = _resolve_products_from_text(text, conversation)
    actions: list[dict[str, Any]] = []
    if "open" in text.lower() or "show" in text.lower():
        url = reverse("assistant:wishlist")
        if language == "ur":
            reply = "Yeh aap ki wishlist hai."
        elif language in {"roman_ur", "mixed"}:
            reply = "Yeh aap ki wishlist hai."
        else:
            reply = "Here is your wishlist."
        return AssistantReply(reply, reply, language, "wishlist", [], [_make_navigation_action("navigate", "Open Wishlist", url)], {})
    if products:
        product = products[0]
        item, created = wishlist.items.get_or_create(product=product)
        reply = f"{product.name} wishlist mein add kar diya gaya hai."
        if language == "en":
            reply = f"{product.name} has been added to your wishlist."
        actions.append({"type": "wishlist_added", "product_id": product.id, "created": created})
        return AssistantReply(reply, reply, language, "wishlist", [_product_to_dict(product)], actions, {"wishlist_count": wishlist.item_count})
    return AssistantReply("I could not identify a product to save.", "I could not identify a product to save.", language, "wishlist", [], actions, {})


def _reply_for_cart(request, text: str, conversation: AIConversation, language: str) -> AssistantReply:
    cart = get_or_create_cart(request)
    if cart is None:
        return _auth_prompt_reply(
            request,
            language,
            "Please log in to your CA-Tech account first. After signing in, I will complete your request.",
            action_type="add_to_cart",
            next_url=request.META.get("HTTP_REFERER") or conversation.source_page or reverse("core:home"),
        )
    products = _resolve_products_from_text(text, conversation)
    product = products[0] if products else None
    lowered = text.lower()
    if "open" in lowered and "cart" in lowered:
        reply = "Opening your cart."
        if language == "ur":
            reply = "Main aap ka cart khol raha hoon."
        elif language in {"roman_ur", "mixed"}:
            reply = "Main aap ka cart khol raha hoon."
        return AssistantReply(reply, reply, language, "cart", [], [_make_navigation_action("navigate", "Open Cart", reverse("cart:detail"))], {})
    if "remove" in lowered and "cart" in lowered:
        if product:
            item = cart.items.filter(product=product).first()
            if item:
                item.delete()
                reply = f"{product.name} cart se remove kar diya gaya hai."
                if language == "en":
                    reply = f"{product.name} has been removed from your cart."
                return AssistantReply(reply, reply, language, "cart", [_product_to_dict(product)], [{"type": "cart_removed", "product_id": product.id}], {"cart_count": cart.item_count})
        reply = "I could not find that item in your cart."
        return AssistantReply(reply, reply, language, "cart", [], [], {})
    if product:
        variant = product.variants.first()
        item, created = cart.items.get_or_create(product=product, variant=variant, defaults={"quantity": 1})
        if not created:
            item.quantity = min(item.quantity + 1, 99)
            item.save(update_fields=["quantity"])
        reply = f"{product.name} cart mein add kar diya gaya hai."
        if language == "en":
            reply = f"{product.name} has been added to your cart."
        actions = [{"type": "cart_added", "product_id": product.id, "quantity": item.quantity, "url": reverse("cart:detail")}]
        return AssistantReply(reply, reply, language, "cart", [_product_to_dict(product)], actions, {"cart_count": cart.item_count})
    return AssistantReply("I could not identify a product to add to your cart.", "I could not identify a product to add to your cart.", language, "cart", [], [], {})


def _reply_for_recommendations(text: str, conversation: AIConversation, language: str) -> AssistantReply:
    use_case = _detect_use_case(text)
    entities = _extract_entities(text)
    budget = entities["budget"] or (Decimal(conversation.memory["budget"]) if conversation.memory.get("budget") else None)
    brand = entities["brand"] or _brand_from_text(conversation.memory.get("brand", ""))
    category = entities["category"] or _category_from_text(conversation.memory.get("category", ""))
    products = search_products(text, budget=budget, brand_name=brand.name if brand else None, category_name=category.name if category else None, limit=4)
    if not products:
        products = list(Product.objects.filter(is_active=True).select_related("brand", "category").prefetch_related("images")[:4])
    if language == "ur":
        header = "Bilkul. Yeh aap ke liye behtareen recommendations hain."
    elif language in {"roman_ur", "mixed"}:
        header = "Bilkul Sir. Yeh aap ke liye behtareen recommendations hain."
    else:
        header = "Absolutely. These are the best recommendations for you."
    lines = [header]
    if use_case:
        lines.append(f"Use case: {use_case}")
    if budget:
        lines.append(f"Budget: {_money(budget)}")
    lines.append("Recommended products:")
    for product in products:
        lines.append(f"- {_format_product_line(product, language)} ({_recommendation_reason(product, use_case, budget)})")
    return AssistantReply(
        text="\n".join(lines),
        voice_text=" ".join(lines),
        language=language,
        intent="recommendation",
        products=[_product_to_dict(product) for product in products],
        actions=[],
        metadata={"use_case": use_case, "budget": str(budget) if budget else None, "product_ids": [product.id for product in products]},
    )


def _reply_for_product_focus(text: str, conversation: AIConversation, language: str) -> AssistantReply:
    product = None
    products = _resolve_products_from_text(text, conversation)
    if products:
        product = products[0]
    else:
        fallback = _last_products_from_memory(conversation)
        product = fallback[0] if fallback else None
    if not product:
        return AssistantReply("I couldn’t find the product you mean.", "I couldn’t find the product you mean.", language, "general", [], [], {})
    text_reply = _product_insight(product, language)
    return AssistantReply(
        text=text_reply,
        voice_text=text_reply,
        language=language,
        intent="product_detail",
        products=[_product_to_dict(product)],
        actions=[],
        metadata={"product_id": product.id},
    )


def get_or_create_wishlist(request) -> Wishlist | None:
    if not request.user.is_authenticated:
        return None
    if not request.session.session_key:
        request.session.create()
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    anonymous = Wishlist.objects.filter(session_key=request.session.session_key, user__isnull=True).first()
    if anonymous and anonymous.id != wishlist.id:
        for item in anonymous.items.all():
            wishlist.items.get_or_create(product=item.product)
        anonymous.delete()
    return wishlist


def execute_request_action(request, conversation: AIConversation, text: str, language: str) -> AssistantReply:
    lowered = text.lower()
    if any(word in lowered for word in ("cart", "bag")) and any(word in lowered for word in ("add", "remove", "open")):
        return _reply_for_cart(request, text, conversation, language)
    if any(word in lowered for word in ("wishlist", "save", "favorite", "favourite")):
        return _reply_for_wishlist(request, text, conversation, language)
    if any(word in lowered for word in ("checkout", "proceed to checkout")):
        return _reply_for_navigation(text, language)
    if any(word in lowered for word in ("profile", "account", "store", "home", "cart")):
        return _reply_for_navigation(text, language)
    return _reply_for_navigation(text, language)


def _provider_reply(settings_obj: AISettings, messages: list[dict[str, str]], language: str) -> str | None:
    if settings_obj.provider == AISettings.PROVIDER_LOCAL:
        return None
    api_key_env = settings_obj.openai_api_key_env if settings_obj.provider == AISettings.PROVIDER_OPENAI else settings_obj.gemini_api_key_env
    api_key = os.getenv(api_key_env, "")
    if not api_key:
        return None
    if settings_obj.provider == AISettings.PROVIDER_OPENAI:
        openai_messages = []
        for m in messages:
            if m["role"] == "system":
                openai_messages.append({"role": "system", "content": m["content"]})
            elif m["role"] == "user":
                openai_messages.append({"role": "user", "content": m["content"]})
            else:
                openai_messages.append({"role": "assistant", "content": m["content"]})
                
        body = json.dumps(
            {
                "model": settings_obj.default_model,
                "messages": openai_messages,
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                payload = json.loads(response.read().decode("utf-8"))
            return payload.get("choices", [])[0].get("message", {}).get("content", "").strip() or None
        except Exception:
            return None
    if settings_obj.provider == AISettings.PROVIDER_GEMINI:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings_obj.default_model}:generateContent?key={api_key}"
        gemini_contents = []
        system_instruction = settings_obj.system_prompt
        for m in messages:
            if m["role"] == "system":
                system_instruction = m["content"]
            else:
                role = "user" if m["role"] == "user" else "model"
                if gemini_contents and gemini_contents[-1]["role"] == role:
                    gemini_contents[-1]["parts"][0]["text"] += "\n\n" + m["content"]
                else:
                    gemini_contents.append({"role": role, "parts": [{"text": m["content"]}]})
                
        body = json.dumps(
            {
                "contents": gemini_contents,
                "systemInstruction": {"parts": [{"text": system_instruction}]},
            }
        ).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                payload = json.loads(response.read().decode("utf-8"))
            candidates = payload.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                return "\n".join(part.get("text", "") for part in parts if part.get("text")).strip() or None
        except Exception:
            return None
    return None


def _reply_for_general(text: str, language: str) -> AssistantReply:
    if language == "ur":
        reply = "Main samajh nahi saka. Main CA-Tech Electronics ka AI assistant hoon. Kya main aapko kuch products dikhaoon?"
    elif language in {"roman_ur", "mixed"}:
        reply = "Main samajh nahi saka. Main CA-Tech Electronics ka AI assistant hoon. Kya main aapko kuch products dikhaoon?"
    else:
        reply = "I'm not sure I understand. I am the CA-Tech Electronics AI assistant. Would you like me to show you some of our latest products?"
    return AssistantReply(reply, reply, language, "general", [], [], {})


def process_assistant_message(request, conversation: AIConversation, message_text: str, is_voice: bool = False) -> AssistantReply:
    settings_obj = get_ai_settings()
    language = detect_language(message_text) if settings_obj.auto_detect_language else (conversation.language or "en")
    intent = _intent_from_text(message_text)
    AIMessage.objects.create(
        conversation=conversation,
        sender=AIMessage.SENDER_USER,
        content=message_text,
        language=language,
        is_voice=is_voice,
        status="sent",
        metadata={"intent": intent},
    )

    if not settings_obj.enabled:
        disabled_text = "The AI Shopping Assistant is currently disabled by the administrator."
        if language == "ur":
            disabled_text = "AI Shopping Assistant filhaal administrator ne disable kiya hua hai."
        elif language in {"roman_ur", "mixed"}:
            disabled_text = "AI Shopping Assistant filhaal administrator ne disable kiya hua hai."
        reply = AssistantReply(disabled_text, disabled_text, language, "disabled", [], [], {})
    else:
        guest_reply = None
        if not request.user.is_authenticated:
            guest_reply = _guest_shopping_reply(request, message_text, conversation, language, intent)
            
        if guest_reply:
            reply = guest_reply
        elif intent == "greeting":
            if request.user.is_authenticated:
                reply = AssistantReply(
                    _authenticated_greeting(request, language),
                    _authenticated_greeting(request, language),
                    language,
                    "greeting",
                    [],
                    [],
                    {
                        "user_name": request.user.get_full_name() or request.user.first_name or request.user.username,
                        "cart_count": get_or_create_cart(request).item_count if get_or_create_cart(request) else 0,
                    },
                )
            else:
                reply = _reply_for_greeting(language)
        elif intent == "compare":
            reply = _reply_for_compare(message_text, conversation, language)
        elif intent == "orders":
            reply = _reply_for_orders(request, request.user, language)
        elif intent in {"cart", "wishlist", "navigation", "add_to_cart", "remove_from_cart", "checkout"}:
            reply = execute_request_action(request, conversation, message_text, language)
        elif intent == "search":
            reply = _reply_for_recommendations(message_text, conversation, language)
        else:
            products = _resolve_products_from_text(message_text, conversation)
            if any(word in message_text.lower() for word in ("camera", "battery", "display", "ram", "storage", "processor")) and products:
                reply = _reply_for_product_focus(message_text, conversation, language)
            elif products:
                reply = _reply_for_recommendations(message_text, conversation, language)
            else:
                reply = _reply_for_general(message_text, language)

    if settings_obj.enabled:
        system_content = settings_obj.system_prompt
        
        system_content += (
            "\n\n[PAYMENT METHODS CAPABILITIES]\n"
            "CA-Tech supports two primary checkout options: Cash on Delivery (COD) and Online Payment.\n"
            "If Online Payment is selected, the gateway automatically adapts to the customer's region:\n"
            "- Pakistan: JazzCash, EasyPaisa, Bank Transfer, Visa, Mastercard.\n"
            "- India: UPI, PhonePe, Paytm, Razorpay, Visa, Mastercard.\n"
            "- International / US Default: Stripe, Google Pay, Apple Pay, PayPal, Visa, Mastercard.\n"
            "Always reassure customers about these secure regional payment options if they ask about payments, checkouts, or security.\n"
        )
        
        try:
            from core.middleware import current_request
            req = current_request.get()
            if req and hasattr(req, 'localization'):
                loc = req.localization
                loc_context = f"Visitor Country: {loc.get('country')}\nVisitor Currency: {loc.get('currency')} ({loc.get('symbol')})\nVisitor Timezone: {loc.get('timezone')}\n"
                system_content += f"\n\n[Visitor Context]\n{loc_context}"
        except Exception:
            pass

        try:
            user_ctx = "Profile: " + ("Logged in as " + (request.user.get_full_name() or request.user.username) if request.user.is_authenticated else "Guest") + "\n"
            if request.user.is_authenticated:
                orders = list(request.user.orders.prefetch_related("items").all()[:5])
                if orders:
                    user_ctx += f"Orders & Shipping Status: {', '.join([f'#{o.order_number} (Shipping: {o.get_status_display()}, Payment: {o.get_payment_status_display()})' for o in orders])}\n"
            
            cart = get_or_create_cart(request)
            if cart is not None and cart.items.exists():
                user_ctx += f"Cart: {', '.join([f'{i.quantity}x {i.product.name}' for i in cart.items.all()])}\n"
                
            wishlist = get_or_create_wishlist(request)
            if wishlist is not None and wishlist.items.exists():
                user_ctx += f"Wishlist: {', '.join([i.product.name for i in wishlist.items.all()])}\n"
                
            from products.models import Category
            cats = Category.objects.all()
            user_ctx += f"Categories & Offers: {', '.join([c.name for c in cats])} (Check products for discounts)\n"
            
            products_match = _resolve_products_from_text(message_text, conversation)
            if not products_match:
                products_match = search_products(message_text, limit=8)
            if not products_match:
                products_match = _last_products_from_memory(conversation)
                
            prod_ctx = ""
            for p in products_match[:8]:
                prod_ctx += f"- {p.name} | Brand: {p.brand.name} | Category: {p.category.name} | Price: {p.price} | Compare/Discount: {p.compare_at_price or 'None'} | Stock: {p.stock} | Specs: {p.specs} | Rating/Reviews: {p.rating} / {p.reviews.count()} reviews\n"
                
            system_content += f"\n\n[LIVE TECHNEST DATABASE]\n{user_ctx}\nRelevant Products Database:\n{prod_ctx if prod_ctx else 'No relevant products found.'}\n"
        except Exception:
            pass

        system_content += f"\n\n[Internal System Results]: {reply.text}\n"
        system_content += "Use the internal system results to formulate your response in a natural conversational tone. "
        system_content += f"Always reply in this language: {language}. If they are from a specific country, adapt your tone, language, and prices to their region. For example, use their local currency for prices."
        
        provider_messages = [{"role": "system", "content": system_content}]
        recent_msgs = list(conversation.messages.exclude(sender=AIMessage.SENDER_SYSTEM).order_by("-created_at")[:15])
        recent_msgs.reverse()
        for msg in recent_msgs:
            role = "user" if msg.sender == AIMessage.SENDER_USER else "assistant"
            provider_messages.append({"role": role, "content": msg.content})
            
        provider_text = _provider_reply(settings_obj, provider_messages, language)
        if provider_text and settings_obj.provider != AISettings.PROVIDER_LOCAL:
            reply.text = provider_text
            reply.voice_text = provider_text

    memory_products = reply.metadata.get("product_ids") or [product["id"] for product in reply.products]
    _update_memory(conversation, message_text, _extract_entities(message_text), memory_products)

    assistant_message = AIMessage.objects.create(
        conversation=conversation,
        sender=AIMessage.SENDER_ASSISTANT,
        content=reply.text,
        language=reply.language,
        is_voice=False,
        status="delivered",
        metadata={"intent": reply.intent, **reply.metadata},
    )
    if is_voice:
        AIVoiceLog.objects.create(
            conversation=conversation,
            user=request.user if request.user.is_authenticated else None,
            transcript=message_text,
            response=reply.text,
            language=reply.language,
            provider=settings_obj.provider,
            success=True,
        )
    conversation.language = reply.language
    conversation.save(update_fields=["language", "last_message_at"])
    return reply


def conversation_payload(conversation: AIConversation, limit: int = 30) -> dict[str, Any]:
    messages = conversation.messages.all().order_by("created_at")[:limit]
    return {
        "conversation_id": conversation.id,
        "language": conversation.language,
        "memory": conversation.memory or {},
        "messages": [
            {
                "id": message.id,
                "sender": message.sender,
                "content": message.content,
                "language": message.language,
                "is_voice": message.is_voice,
                "status": message.status,
                "created_at": message.created_at.isoformat(),
                "metadata": message.metadata,
            }
            for message in messages
        ],
    }


def build_conversation(request, conversation_id: int | None = None) -> AIConversation:
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    conversation = None
    if conversation_id:
        conversation = AIConversation.objects.filter(id=conversation_id).first()
    if not conversation:
        conversation = (
            AIConversation.objects.filter(session_key=session_key, user=request.user if request.user.is_authenticated else None)
            .order_by("-last_message_at")
            .first()
        )
    if not conversation:
        conversation = AIConversation.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_key=session_key,
            title="Shopping Assistant",
            language="en",
            source_page=request.headers.get("Referer", "")[:300],
        )
        settings_obj = get_ai_settings()
        AIMessage.objects.create(
            conversation=conversation,
            sender=AIMessage.SENDER_ASSISTANT,
            content=settings_obj.welcome_message,
            language="en",
            status="delivered",
            metadata={"intent": "welcome"},
        )
    return conversation


def summarize_conversation(conversation: AIConversation) -> str:
    memory = conversation.memory or {}
    budget = memory.get("budget")
    brand = memory.get("brand")
    category = memory.get("category")
    bits = []
    if budget:
        bits.append(f"Budget {budget}")
    if brand:
        bits.append(f"Brand {brand}")
    if category:
        bits.append(f"Category {category}")
    return ", ".join(bits) if bits else "No active preference"
