from django.contrib import admin
from django.urls import path, include
from app import views
from django.conf import settings
from django.conf.urls.static import static
from app.views import (
    login_view,
    home_view,
    logout_view,
    login_code_confirm_view,
    PasswordResetCustomView,
    PasswordResetDoneCustomView,
    PasswordResetConfirmCustomView,
    PasswordResetCompleteCustomView,
    verify_email_view,
    verification_sent_view,
    resend_verification_view, 
)
from produtos.views import sobre

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('', include('app.urls')),
    path('sobre/', sobre, name='sobre'),
    path('contato/', views.contato_view, name='contato'),
    path('login/', login_view, name='login'),
    path('verificar-email/<uidb64>/<token>/', verify_email_view, name='verify_email'),
    path('verificacao-enviada/', verification_sent_view, name='verification_email'),
    path('reenviar-verificacao/<int:user_id>/', resend_verification_view, name='resend_verification'),
    path('logout/', logout_view, name='logout'),
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