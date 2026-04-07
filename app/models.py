from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.signals import pre_delete
import uuid


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    # Dados pessoais
    nome_completo = models.CharField(max_length=200, blank=True)
    cpf = models.CharField(max_length=14, blank=True)
    telefone = models.CharField(max_length=20, blank=True, verbose_name="WhatsApp / Telefone")

    # Verificação de e-mail
    email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)

    # Endereço
    cep = models.CharField(max_length=9, blank=True)
    rua = models.CharField(max_length=200, blank=True)
    numero = models.CharField(max_length=20, blank=True)
    complemento = models.CharField(max_length=200, blank=True)
    bairro = models.CharField(max_length=100, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True)

    def __str__(self):
        return f"Perfil de {self.user.email}"

    def get_cpf_formatado(self):
        """Retorna o CPF formatado (XXX.XXX.XXX-XX)"""
        if not self.cpf:
            return ''
        cpf_limpo = ''.join(filter(str.isdigit, self.cpf))
        if len(cpf_limpo) == 11:
            return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
        return self.cpf

    def save(self, *args, **kwargs):
        """Salva o CPF sem formatação no banco"""
        if self.cpf:
            self.cpf = ''.join(filter(str.isdigit, self.cpf))
        # Salva telefone só com dígitos também
        if self.telefone:
            self.telefone = ''.join(filter(str.isdigit, self.telefone))
        super().save(*args, **kwargs)


class LoginCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.used and timezone.now() < self.expires_at

    @classmethod
    def create_code(cls, email, code):
        return cls.objects.create(
            email=email,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=10)
        )


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_tokens')
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.used and timezone.now() < self.expires_at

    @classmethod
    def create_token(cls, user):
        return cls.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(days=7)
        )


@receiver(post_save, sender=User)
def criar_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(pre_delete, sender=User)
def deletar_relacionados(sender, instance, **kwargs):
    from app.models import EmailVerificationToken, UserProfile
    EmailVerificationToken.objects.filter(user=instance).delete()
    UserProfile.objects.filter(user=instance).delete()