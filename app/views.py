from django.shortcuts import render
# from django.contrib.auth.decorators import login_required


def home_view(request):
    return render(request, 'pages/home.html')

def cadernetas_view(request):
    return render(request, 'pages/cadernetas.html')

def lembrancinhas_view(request):
    return render(request, 'pages/lembrancinhas.html')

def personalizados_view(request):
    return render(request, 'pages/personalizados.html')

def sobre_view(request):
    return render(request, 'pages/sobre.html')

def contato_view(request):
    return render(request, 'pages/contato.html')



# Create your views here.
