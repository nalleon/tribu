from django import forms
from .models import Wave


class EditWaveForm(forms.ModelForm):
    class Meta:
        model = Wave
        fields = ('content',)
