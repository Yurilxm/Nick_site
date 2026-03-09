from django.contrib import admin
from django.urls import path, include
from app import views
from django.conf import settings
from django.conf.urls.static import static
from app.views import (
    LoginCustomView,
    home_view,
    logout_view,
    register_view,
    login_code_confirm_view,
    PasswordResetCustomView,
    PasswordResetDoneCustomView,
    PasswordResetConfirmCustomView,
    PasswordResetCompleteCustomView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('sobre/', views.sobre_view, name='sobre'),
    path('contato/', views.contato_view, name='contato'),
    path('login/', LoginCustomView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('cadastro/', register_view, name='register'),
    path('produtos/', include('produtos.urls')),
    path('carrinho/', include('carrinho.urls')),
    path('marketing/', include('marketing.urls')),
    path('esqueceu-senha/', PasswordResetCustomView.as_view(), name='password_reset'),
    path('esqueceu-senha/enviado/', PasswordResetDoneCustomView.as_view(), name='password_reset_done'),
    path('resetar-senha/<uidb64>/<token>/', PasswordResetConfirmCustomView.as_view(), name='password_reset_confirm'),
    path('resetar-senha/sucesso', PasswordResetCompleteCustomView.as_view(), name='password_reset_complete'),
    path('login/codigo/', views.login_email_code_view, name='login_email_code'),
    path('login/codigo/enviar/', views.send_login_code_view, name='login_code_send'),
    path('login-codigo/confirmar/', login_code_confirm_view, name='login_code_confirm'),
    path('buscar-produtos/', views.search_products_view, name='search_products'),
    path('pedidos/', include('pedidos.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)