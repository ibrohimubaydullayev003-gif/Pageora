from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import Website, Profile


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Email manzilingiz'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Foydalanuvchi nomi'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Parol'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Parolni tasdiqlang'
        })


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Foydalanuvchi nomi'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Parol'
        })


class WebsiteForm(forms.ModelForm):
    class Meta:
        model = Website
        fields = [
            'title', 'meta_title', 'meta_description',
            'logo', 'favicon',
            'background_color', 'text_color', 'accent_color',
            'hero_title', 'hero_subtitle', 'hero_button_text', 'hero_button_link',
            'about_title', 'about_content',
            'services_title', 'services_content',
            'contact_title', 'contact_email', 'contact_phone',
            'contact_address', 'contact_telegram', 'contact_instagram',
            'custom_css', 'is_published'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'meta_title': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_description': forms.TextInput(attrs={'class': 'form-control'}),
            'background_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'text_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'accent_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'hero_title': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'hero_subtitle': forms.TextInput(attrs={'class': 'form-control'}),
            'hero_button_text': forms.TextInput(attrs={'class': 'form-control'}),
            'hero_button_link': forms.TextInput(attrs={'class': 'form-control'}),
            'about_title': forms.TextInput(attrs={'class': 'form-control'}),
            'about_content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'services_title': forms.TextInput(attrs={'class': 'form-control'}),
            'services_content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Har bir xizmatni yangi qatordan yozing'}),
            'contact_title': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_address': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_telegram': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '@username'}),
            'contact_instagram': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'username'}),
            'custom_css': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'favicon': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio']
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }