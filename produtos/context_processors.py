from .models import Categoria

def categorias_menu(request):
    categorias = Categoria.objects.all()
    return {
        "categorias_menu": categorias
    }