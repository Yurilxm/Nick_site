"""
URL configuration for site_nick project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from app import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from app.views import LoginCustomView, home_view, logout_view
from app.views import register_view, login_code_confirm_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('sobre/', views.sobre_view, name='sobre'),
    path('contato/', views.contato_view, name='contato'),
    path('login/', LoginCustomView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('cadastro/', register_view, name='register'),
    path('produtos/', include('produtos.urls')),
    path('carrinho/', include('carrinho.urls')),
    path("marketing/", include("marketing.urls")),
    path('esqueceu-senha/', auth_views.PasswordResetView.as_view(template_name='auth/password_reset.html'), name='password_reset'),
    path('esqueceu-senha/enviado/', auth_views.PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'), name='password_reset_done'),
    path('resetar-senha/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='auth/password_reset_confirm.html'), name='password_reset_confirm'),
    path('resetar-senha/sucesso', auth_views.PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'), name='password_reset_complete'),
    path('login/codigo/', views.login_email_code_view, name='login_email_code'),
    path('login/codigo/enviar/', views.send_login_code_view, name='login_code_send'),
    path('login-codigo/confirmar/', login_code_confirm_view, name='login_code_confirm'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)