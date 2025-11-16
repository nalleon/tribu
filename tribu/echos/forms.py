from django import forms
from .models import Echo
from waves.models import Wave

class AddEchoForm(forms.ModelForm):
    class Meta:
        model = Echo
        fields = ('content',)

    def save(self, user, *args, **kwargs):
        echo = super().save(commit=False)
        echo.user = user
        echo = super().save(*args, **kwargs)
        return echo

class EditEchoForm(forms.ModelForm):
    class Meta:
        model = Echo
        fields = ('content',)


class AddWaveForm(forms.ModelForm):
    class Meta:
        model = Wave
        fields = ('content',)
