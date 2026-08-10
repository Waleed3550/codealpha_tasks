from django import forms

from orders.models import Order
from products.models import Brand, Category, Product, ProductImage


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={"multiple": True}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        if not data:
            return []
        files = data if isinstance(data, (list, tuple)) else [data]
        return [super(MultipleFileField, self).clean(file, initial) for file in files]


class ProductForm(forms.ModelForm):
    image_urls = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "One image URL per line"}),
        help_text="Optional. Paste one image URL per line.",
    )
    uploaded_images = MultipleFileField(required=False)

    class Meta:
        model = Product
        fields = (
            "category",
            "brand",
            "name",
            "slug",
            "short_description",
            "description",
            "price",
            "compare_at_price",
            "sku",
            "stock",
            "rating",
            "warranty",
            "specs",
            "is_active",
            "is_featured",
        )
        widgets = {"description": forms.Textarea(attrs={"rows": 5}), "specs": forms.Textarea(attrs={"rows": 4})}


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name", "slug", "description", "image_url", "is_active")


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ("name", "slug", "description", "logo_url", "is_featured")


class StockUpdateForm(forms.Form):
    stock = forms.IntegerField(min_value=0)


class OrderNoteForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("internal_notes",)
        widgets = {"internal_notes": forms.Textarea(attrs={"rows": 4})}
