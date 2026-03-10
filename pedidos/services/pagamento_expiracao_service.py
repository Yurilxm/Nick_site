from django.utils import timezone
from pedidos.models import Pagamento


def expirar_pix_vencidos():

    pagamentos = Pagamento.objects.filter(
        metodo="pix",
        status="pendente",
        pix_expira_em__lt=timezone.now()
    )

    for pagamento in pagamentos:

        pagamento.status = "recusado"
        pagamento.save()

        pedido = pagamento.pedido

        pedido.status = "expirado"
        pedido.save()