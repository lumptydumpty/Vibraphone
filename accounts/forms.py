from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("username", "email", "name", "location", "bio", "contact_info", "links", "profile_image")

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("name", "location", "bio", "contact_info", "links", "profile_image")
