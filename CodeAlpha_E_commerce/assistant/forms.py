from django import forms

from assistant.models import AISettings


LANGUAGE_CHOICES = [
    ("en", "English"),
    ("ur", "Urdu"),
    ("roman_ur", "Roman Urdu"),
    ("roman_en", "Roman English"),
    ("mixed", "Mixed Urdu English"),
]

PROVIDER_CHOICES = [
    (AISettings.PROVIDER_LOCAL, "Local Rules Engine"),
    (AISettings.PROVIDER_OPENAI, "OpenAI Responses API"),
    (AISettings.PROVIDER_GEMINI, "Google Gemini API"),
]


class AISettingsForm(forms.ModelForm):
    supported_languages = forms.MultipleChoiceField(
        choices=LANGUAGE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = AISettings
        fields = (
            "assistant_name",
            "enabled",
            "provider",
            "default_model",
            "openai_api_key_env",
            "gemini_api_key_env",
            "system_prompt",
            "welcome_message",
            "supported_languages",
            "voice_enabled",
            "auto_detect_language",
        )
        widgets = {
            "system_prompt": forms.Textarea(attrs={"rows": 8}),
            "welcome_message": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.supported_languages:
            self.initial["supported_languages"] = self.instance.supported_languages

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.supported_languages = self.cleaned_data.get("supported_languages", [])
        if commit:
            instance.save()
        return instance
