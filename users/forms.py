from django import forms
 
class UserRegistrationForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'placeholder': 'Your full name'}))
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'placeholder': 'your@email.com'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Choose a password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Repeat password'}))
 
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        if password and confirm and password != confirm:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data
