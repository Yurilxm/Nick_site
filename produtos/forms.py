from django import forms
from .models import Avaliacao


class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = ["nome", "comentario", "estrelas", "foto"]

        widgets = {
            "nome": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Seu nome"
            }),
            "comentario": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Conte como foi sua experiência...",
                "rows": 4
            }),
            # estrelas é renderizado manualmente no template como estrelas clicáveis
            "estrelas": forms.HiddenInput(),
        }