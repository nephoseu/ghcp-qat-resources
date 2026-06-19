from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"id": "username-input"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"id": "password-input"}))


class TicketForm(forms.Form):
    title = forms.CharField(max_length=200, widget=forms.TextInput(attrs={"id": "ticket-title-input"}))
    description = forms.CharField(widget=forms.Textarea(attrs={"id": "ticket-description-input", "rows": 4}))
