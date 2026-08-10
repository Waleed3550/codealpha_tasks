"""
fix_product_images.py
─────────────────────
Replaces all random picsum.photos URLs with real, category-appropriate
tech product images from Unsplash (specific photo IDs).

Each product gets images determined by:
  hash(product.slug) % len(pool)  → always the same image for the same product

Usage:
    python manage.py fix_product_images
    python manage.py fix_product_images --dry-run
"""
from __future__ import annotations

import hashlib

from django.core.management.base import BaseCommand

from products.models import ProductImage

# ─────────────────────────────────────────────────────────────────────────────
# Curated Unsplash pools — one pool per category.
# Every URL is a known, publicly accessible Unsplash photo.
# FORMAT: ?auto=format&fit=crop&w=800&q=80  gives a clean 800px JPEG.
# ─────────────────────────────────────────────────────────────────────────────

BASE = "https://images.unsplash.com/photo-"
Q    = "?auto=format&fit=crop&w=800&q=80"

POOLS: dict[str, list[str]] = {

    # ── Smartphones ──────────────────────────────────────────────────────────
    "smartphones": [
        BASE + "1511707171634-5f897ff02aa9" + Q,   # array of colorful phones
        BASE + "1592750475338-74b7b21085ab" + Q,   # Samsung-style phone in hand
        BASE + "1580910051074-3eb694886505" + Q,   # hand holding phone
        BASE + "1556656793-08538906a9f8"   + Q,   # clean black phone
        BASE + "1574944985070-8f3ebc6b79d2" + Q,  # phone photography session
        BASE + "1598327105666-5b89351aff97" + Q,  # modern phone on surface
        BASE + "1567581935884-3349723552ca" + Q,  # person using phone
        BASE + "1512941937669-90a1b58e7e9c" + Q,  # iPhone in use
        BASE + "1601784551446-20c9e07cdbdb" + Q,  # clean modern phone
        BASE + "1565849904461-04a58ad377e0" + Q,  # phone flat lay
        BASE + "1605236453806-6ff36851218e" + Q,  # Samsung Galaxy flat lay
        BASE + "1610945264803-3d18a9f3c57d" + Q,  # iPhone side view
        BASE + "1585060544812-6b45742d762f" + Q,  # many phones comparison
        BASE + "1477090996503-ec6bf09a02e5" + Q,  # phone on desk
        BASE + "1525048155-d2af2d4c11a5"   + Q,  # phone and coffee
        BASE + "1550009158-9ebf69173e03"   + Q,  # multiple phones
        BASE + "1520923642038-b46c15e3f7e5" + Q,  # phone in pocket
        BASE + "1533228100845-08145b01de14" + Q,  # phone closeup lens
        BASE + "1508921340878-ba53e1f016ec" + Q,  # three phones flat lay
        BASE + "1444653614732-0e7d7de27b9f" + Q,  # person texting
    ],

    # ── Laptops ───────────────────────────────────────────────────────────────
    "laptops": [
        BASE + "1496181133206-80ce9b88a853" + Q,  # open laptop side view
        BASE + "1517336714731-489689fd1ca8" + Q,  # MacBook on wooden table
        BASE + "1593642632559-0c6d3fc62b89" + Q,  # laptop workspace
        BASE + "1525547719571-a2d4ac8945e2" + Q,  # laptop keyboard close-up
        BASE + "1484788984921-03950022c9ef" + Q,  # laptop desk setup
        BASE + "1541807084-5c52b6b3adef"   + Q,  # laptop keyboard angle
        BASE + "1498050108023-c5249f4df085" + Q,  # coding on laptop
        BASE + "1603302576837-37561b2e2302" + Q,  # gaming laptop RGB
        BASE + "1588702547919-26089e690ecc" + Q,  # dark theme laptop
        BASE + "1544731612-de7f96afe55f"   + Q,  # laptop setup with plant
        BASE + "1468436139062-f60851436293" + Q,  # laptop on minimalist table
        BASE + "1537498425277-c283d32ef9db" + Q,  # thin silver laptop
        BASE + "1611532736597-de2d4265fba3" + Q,  # laptop and monitor
        BASE + "1555774698-0b77e0d5fac6"   + Q,  # laptop wireframe
        BASE + "1526406915894-7bcd65f60845" + Q,  # laptop in office
        BASE + "1486312338219-ce68d2c6f44d" + Q,  # laptop person typing
    ],

    # ── Gaming ────────────────────────────────────────────────────────────────
    "gaming": [
        BASE + "1542751371-adc38448a05e"   + Q,  # full gaming setup RGB
        BASE + "1593305841991-05c297ba4575" + Q,  # PlayStation controller
        BASE + "1612287230202-1ff1d85d1bdf" + Q,  # gaming keyboard RGB
        BASE + "1558618666-fcd25c85cd64"   + Q,  # gaming mouse
        BASE + "1616588589676-62b3bd4ff6d2" + Q,  # gaming monitor desk
        BASE + "1552820728-8b83bb6b773f"   + Q,  # gaming room setup
        BASE + "1587202372775-e229f172b9d7" + Q,  # gaming PC build
        BASE + "1538481199705-c710c4e965fc" + Q,  # gamer at PC
        BASE + "1600861194802-a2b11076bc51" + Q,  # controller in hand
        BASE + "1523987961887-2d4f28c7e3d0" + Q,  # gaming headset
        BASE + "1634193295627-1cddff751aeb" + Q,  # gaming chair
        BASE + "1569144157591-c60f3f82f38b" + Q,  # gaming laptop angle
    ],

    # ── Audio ─────────────────────────────────────────────────────────────────
    "audio": [
        BASE + "1505740420928-5e560c06d30e" + Q,  # headphones on surface
        BASE + "1484704849700-f032a568e944" + Q,  # overhead headphones
        BASE + "1546435770-a3e426bf472b"   + Q,  # wireless earbuds white
        BASE + "1572536147248-ac59a8abfa4b" + Q,  # Bluetooth speaker
        BASE + "1608043152269-423dbba4e7e1" + Q,  # TWS earbuds case
        BASE + "1590658268037-6bf12165a8df" + Q,  # dark headphones
        BASE + "1524678606370-a47ad25cb82a" + Q,  # compact speaker
        BASE + "1583394838336-acd977736f90" + Q,  # earbuds flat lay
        BASE + "1613040809024-b4ef7ba99bc3" + Q,  # earbuds case open
        BASE + "1558756520-22cfe5d382ca"   + Q,  # wireless earbuds black
        BASE + "1509440159596-0249088772ff" + Q,  # over-ear headphones stand
        BASE + "1619983081593-e2ba5b543168" + Q,  # studio monitor speakers
    ],

    # ── Displays ──────────────────────────────────────────────────────────────
    "displays": [
        BASE + "1527443224154-c4a573d5f5f6" + Q,  # monitor desk clean
        BASE + "1593640408182-31c228eb4e8a" + Q,  # monitor setup
        BASE + "1614624532983-4ce03382d63d" + Q,  # ultrawide monitor
        BASE + "1547119957-637f8679db1e"   + Q,  # dual monitor setup
        BASE + "1585771724684-38269d6639fd" + Q,  # gaming monitor RGB
        BASE + "1609081219090-a6d81d3085bf" + Q,  # curved monitor
        BASE + "1611532736597-de2d4265fba3" + Q,  # laptop + monitor desk
        BASE + "1551645120-d70bfe84c826"   + Q,  # multiple screens wall
        BASE + "1573148195900-7845dcb0db05" + Q,  # widescreen monitor
        BASE + "1586210579191-33b45e38fa2c" + Q,  # curved gaming monitor
    ],

    # ── Accessories ────────────────────────────────────────────────────────────
    "accessories": [
        BASE + "1625772452859-1c03d5bf1137" + Q,  # phone cases colorful
        BASE + "1609921212029-bb5a28e60960" + Q,  # wireless charger pad
        BASE + "1601999109332-2b54ae24c1f9" + Q,  # USB hub/dock
        BASE + "1583394838336-acd977736f90" + Q,  # cable accessories
        BASE + "1585060544812-6b45742d762f" + Q,  # phone accessories flat
        BASE + "1591337676887-a217a6970a8a" + Q,  # charging cables
        BASE + "1523987961887-2d4f28c7e3d0" + Q,  # tech gadgets
        BASE + "1546435770-a3e426bf472b"   + Q,  # earbuds (accessory)
        BASE + "1609081219090-a6d81d3085bf" + Q,  # power bank
        BASE + "1558618666-fcd25c85cd64"   + Q,  # peripheral
        BASE + "1506794778202-cad84cf45f1d" + Q,  # person holding gadget
        BASE + "1517336714731-489689fd1ca8" + Q,  # desk tech setup
    ],

    # ── Fallback (unknown category) ────────────────────────────────────────────
    "default": [
        BASE + "1496181133206-80ce9b88a853" + Q,
        BASE + "1517336714731-489689fd1ca8" + Q,
        BASE + "1542751371-adc38448a05e"   + Q,
        BASE + "1505740420928-5e560c06d30e" + Q,
        BASE + "1527443224154-c4a573d5f5f6" + Q,
    ],
}

# Map category slugs / name fragments → pool key
CATEGORY_MAP: dict[str, str] = {
    "smartphone": "smartphones",
    "phone":      "smartphones",
    "mobile":     "smartphones",
    "laptop":     "laptops",
    "notebook":   "laptops",
    "computer":   "laptops",
    "gaming":     "gaming",
    "game":       "gaming",
    "audio":      "audio",
    "headphone":  "audio",
    "speaker":    "audio",
    "earbuds":    "audio",
    "display":    "displays",
    "monitor":    "displays",
    "screen":     "displays",
    "accessory":  "accessories",
    "accessories":"accessories",
    "cable":      "accessories",
    "charger":    "accessories",
    "case":       "accessories",
}


def _pool_key(category_name: str) -> str:
    name = category_name.lower()
    for keyword, key in CATEGORY_MAP.items():
        if keyword in name:
            return key
    return "default"


def _pick(slug: str, pool: list[str], offset: int = 0) -> str:
    """Deterministically pick an image from the pool using the product slug."""
    digest = int(hashlib.md5(slug.encode()).hexdigest(), 16)
    return pool[(digest + offset) % len(pool)]


class Command(BaseCommand):
    help = "Replace random picsum images with real category-appropriate tech photos."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview changes without writing to the database.",
        )

    def handle(self, *args, **options):
        dry_run: bool = options["dry_run"]

        images = (
            ProductImage.objects
            .select_related("product__category")
            .all()
        )

        total   = images.count()
        updated = 0
        skipped = 0

        self.stdout.write(f"Processing {total} product images …\n")

        bulk: list[ProductImage] = []

        for img in images:
            product  = img.product
            cat_name = product.category.name if product.category else "default"
            pool_key = _pool_key(cat_name)
            pool     = POOLS[pool_key]
            slug     = product.slug

            # Primary image uses offset 0; other images rotate through the pool
            offset = img.sort_order if img.sort_order else (0 if img.is_primary else img.id % len(pool))
            new_url = _pick(slug, pool, offset)

            if img.image_url == new_url:
                skipped += 1
                continue

            if dry_run:
                self.stdout.write(
                    f"  [DRY] {product.name[:40]:40s} -> {new_url[:60]}"
                )
            else:
                img.image_url = new_url
                bulk.append(img)

            updated += 1

            # Batch write every 500 records
            if not dry_run and len(bulk) >= 500:
                ProductImage.objects.bulk_update(bulk, ["image_url"])
                self.stdout.write(f"  … saved {len(bulk)} images")
                bulk.clear()

        # Final batch
        if not dry_run and bulk:
            ProductImage.objects.bulk_update(bulk, ["image_url"])

        verb = "Would update" if dry_run else "Updated"
        self.stdout.write(
            self.style.SUCCESS(
                f"\n[OK] {verb} {updated} images, {skipped} already correct. "
                f"Total processed: {total}"
            )
        )
