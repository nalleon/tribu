from django import forms
from .models import Profile

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar', 'bio')

    def save(self, user, *args, **kwargs):
        profile = super().save(commit=False)
        profile.user = user
        profile = super().save(*args, **kwargs)
        return profile
