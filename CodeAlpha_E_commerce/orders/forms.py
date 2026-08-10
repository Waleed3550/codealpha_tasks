from django import forms


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=160)
    email = forms.EmailField()
    phone = forms.CharField(max_length=24)
    billing_address = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}))
    shipping_address = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}))
    city = forms.CharField(max_length=80)
    state = forms.CharField(max_length=80)
    postal_code = forms.CharField(max_length=20)
    country = forms.CharField(max_length=80, initial="United States")
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))
    payment_method = forms.ChoiceField(
        choices=[("cod", "Cash on Delivery"), ("card", "Online Payment")],
        widget=forms.RadioSelect(attrs={"class": "payment-radio"}),
        initial="cod"
    )
