from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

from .models import Pedido
from produtos.models import Opcao


def gerar_ficha_pdf(request, pedido_id):

    pedido = Pedido.objects.get(id=pedido_id)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="pedido_{pedido.id}.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    elementos = []

    elementos.append(Paragraph(f"<b>PEDIDO #{pedido.id}</b>", styles["Title"]))
    elementos.append(Spacer(1, 20))

    elementos.append(Paragraph(f"<b>Cliente:</b> {pedido.usuario}", styles["Normal"]))
    elementos.append(Paragraph(f"<b>CEP:</b> {pedido.cep_entrega}", styles["Normal"]))
    elementos.append(Paragraph(f"<b>Endereço:</b> {pedido.rua}, {pedido.numero}", styles["Normal"]))
    elementos.append(Paragraph(f"<b>Bairro:</b> {pedido.bairro}", styles["Normal"]))
    elementos.append(Paragraph(f"<b>Cidade:</b> {pedido.cidade}/{pedido.estado}", styles["Normal"]))

    elementos.append(Spacer(1, 20))
    elementos.append(Paragraph("<b>Itens do pedido</b>", styles["Heading2"]))
    elementos.append(Spacer(1, 10))

    for item in pedido.itens.all():

        elementos.append(Paragraph(f"<b>Produto:</b> {item.produto.nome}", styles["Normal"]))
        elementos.append(Paragraph(f"<b>Quantidade:</b> {item.quantidade}", styles["Normal"]))

        if item.opcoes:

            elementos.append(Paragraph("<b>Personalização:</b>", styles["Normal"]))

            for chave, valor in item.opcoes.items():

                try:
                    opcao = Opcao.objects.get(id=valor)
                    valor_final = opcao.nome
                except:
                    valor_final = valor

                elementos.append(
                    Paragraph(f"{chave.capitalize()}: {valor_final}", styles["Normal"])
                )

        elementos.append(Spacer(1, 10))

    doc.build(elementos)

    return response