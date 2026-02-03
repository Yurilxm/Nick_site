from django.urls import path
from .views import cadastrar_email_marketing

urlpatterns = [
    path("email/cadastrar/", cadastrar_email_marketing, name="cadastrar_email_marketing"),
]