import re
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

User = get_user_model()


class RegisterForm(forms.Form):
    nome = forms.CharField(
        label='Nome completo',
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Nome completo'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'Email'})
    )
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'placeholder': 'Senha'})
    )
    password2 = forms.CharField(
        label='Confirmar senha',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar senha'})
    )

    def clean_nome(self):
        nome = self.cleaned_data.get('nome', '').strip()
        if len(nome) < 2:
            raise ValidationError('Nome deve ter pelo menos 2 caracteres.')
        # Verifica se o nome contém números e bloqueia se encontrar
        if re.search(r'\d', nome):
            raise ValidationError('Nome não pode conter números.')
        # Só permite letras (com acentuação), espaços e hífens
        if not re.fullmatch(r"[^\W\d_][\w'\- ]*", nome, re.UNICODE):
            raise ValidationError('Nome deve conter apenas letras.')
        return nome

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()

        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError('Informe um e-mail válido (ex: seu@email.com).')

        domain = email.split('@')[-1]
        if '.' not in domain:
            raise ValidationError('Informe um e-mail válido (ex: seu@email.com).')

        if User.objects.filter(email=email).exists():
            raise ValidationError('Este e-mail já está cadastrado.')

        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        errors = []

        if password1 and len(password1) < 8:
            errors.append('A senha deve conter pelo menos 8 caracteres.')

        if password1 and password2 and password1 != password2:
            errors.append('As senhas não coincidem.')

        if errors:
            raise ValidationError(' '.join(errors))

        return cleaned_data


class LoginForm(AuthenticationForm):
    remember = forms.BooleanField(
        label='Lembre-me',
        required=False,
        widget=forms.CheckboxInput(attrs={'id': 'remember'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Email'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Senha'})

    def clean(self):
        username = self.cleaned_data.get('username', '').strip().lower()
        password = self.cleaned_data.get('password')

        if not username:
            raise forms.ValidationError('Informe seu e-mail.')

        if not password:
            raise forms.ValidationError('Informe sua senha.')

        try:
            validate_email(username)
        except ValidationError:
            raise forms.ValidationError('Informe um e-mail válido.')

        domain = username.split('@')[-1]
        if '.' not in domain:
            raise forms.ValidationError('Informe um e-mail válido (ex: seu@email.com).')

        user = authenticate(username=username, password=password)
        if user is None:
            raise forms.ValidationError('E-mail ou senha incorretos.')
        elif not user.is_active:
            raise forms.ValidationError('Esta conta está desativada.')

        self.user_cache = user
        return self.cleaned_data