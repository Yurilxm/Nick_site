from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.colors import HexColor
import os

from .models import Pedido
from produtos.models import Opcao, GrupoOpcao


PINK = HexColor('#ff85a1')
LILAC = HexColor('#b695c0')
BABY_PINK = HexColor('#ffafcc')
BABY_LILAC = HexColor('#cdb4db')
TEXT_DARK = HexColor('#4a3f5c')
TEXT_MID = HexColor('#7a6a8a')
TEXT_LIGHT = HexColor('#c4b5d0')
BG_LIGHT = HexColor('#fff9fc')
WHITE = HexColor('#ffffff')
BORDER = HexColor('#e8d5f0')


def gerar_ficha_pdf(request, pedido_id):
    pedido = Pedido.objects.get(id=pedido_id)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="pedido_{pedido.id}.pdf"'

    width, height = A4
    c = canvas.Canvas(response, pagesize=A4)

    # ==========================================
    # HEADER — fundo gradiente rosa/lilás
    # ==========================================
    header_height = 4.5 * cm

    # Fundo do header
    c.setFillColor(BABY_PINK)
    c.rect(0, height - header_height, width, header_height, fill=1, stroke=0)

    # Faixa lilás decorativa
    c.setFillColor(BABY_LILAC)
    c.rect(0, height - header_height, width * 0.4, header_height, fill=1, stroke=0)

    # Círculo decorativo
    c.setFillColor(HexColor('#ffd6e7'))
    c.circle(width - 3 * cm, height - header_height / 2, 2.5 * cm, fill=1, stroke=0)
    c.setFillColor(HexColor('#e8c8f0'))
    c.circle(width - 3 * cm, height - header_height / 2, 1.8 * cm, fill=1, stroke=0)

    # Nome da loja
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(1.5 * cm, height - 2 * cm, "Nick Brindes")

    c.setFont("Helvetica", 11)
    c.setFillColor(HexColor('#ffe0ec'))
    c.drawString(1.5 * cm, height - 2.8 * cm, "Ficha de Producao")

    # Número do pedido (canto direito)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(width - 1.5 * cm, height - 1.8 * cm, f"PEDIDO #{pedido.id}")

    c.setFont("Helvetica", 9)
    c.setFillColor(HexColor('#ffe0ec'))
    data_criacao = pedido.criado_em.strftime("%d/%m/%Y %H:%M") if pedido.criado_em else ""
    c.drawRightString(width - 1.5 * cm, height - 2.5 * cm, data_criacao)

    # Status badge
    status_cores = {
        "pago": (HexColor('#d4f7e0'), HexColor('#2d7a4f')),
        "em_producao": (HexColor('#dde8ff'), HexColor('#2d4a9b')),
        "enviado": (HexColor('#f0e0ff'), HexColor('#6a2d9b')),
        "aguardando_pagamento": (HexColor('#fff3cd'), HexColor('#856404')),
        "cancelado": (HexColor('#fde8e8'), HexColor('#9b2d2d')),
    }
    bg_status, fg_status = status_cores.get(pedido.status, (HexColor('#f0f0f0'), HexColor('#666666')))
    status_texto = pedido.get_status_display().upper()

    c.setFillColor(bg_status)
    c.roundRect(width - 5 * cm, height - 3.6 * cm, 3.5 * cm, 0.7 * cm, 5, fill=1, stroke=0)
    c.setFillColor(fg_status)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(width - 3.25 * cm, height - 3.2 * cm, status_texto)

    # ==========================================
    # SEÇÃO: DADOS DO CLIENTE
    # ==========================================
    y = height - header_height - 1 * cm

    def secao_titulo(titulo, y_pos):
        # Linha decorativa
        c.setFillColor(BABY_PINK)
        c.rect(1.5 * cm, y_pos - 0.1 * cm, 0.3 * cm, 0.8 * cm, fill=1, stroke=0)
        c.setFillColor(TEXT_DARK)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2.2 * cm, y_pos + 0.1 * cm, titulo)
        # Linha separadora
        c.setStrokeColor(BORDER)
        c.setLineWidth(0.5)
        c.line(1.5 * cm, y_pos - 0.3 * cm, width - 1.5 * cm, y_pos - 0.3 * cm)
        return y_pos - 0.8 * cm

    def campo(label, valor, x, y_pos, largura=8 * cm):
        c.setFillColor(TEXT_LIGHT)
        c.setFont("Helvetica", 8)
        c.drawString(x, y_pos + 0.3 * cm, label.upper())
        c.setFillColor(TEXT_DARK)
        c.setFont("Helvetica", 10)
        c.drawString(x, y_pos, str(valor) if valor else "—")

    y = secao_titulo("Dados do Cliente", y)
    y -= 0.3 * cm

    cliente_nome = pedido.usuario.get_full_name() or pedido.usuario.username if pedido.usuario else "—"
    cliente_email = pedido.usuario.email if pedido.usuario else "—"

    campo("Nome", cliente_nome, 1.5 * cm, y)
    campo("E-mail", cliente_email, 10 * cm, y)
    y -= 1 * cm

    # ==========================================
    # SEÇÃO: ENDEREÇO DE ENTREGA
    # ==========================================
    y -= 0.3 * cm
    y = secao_titulo("Endereco de Entrega", y)
    y -= 0.3 * cm

    if pedido.cep_entrega:
        campo("CEP", pedido.cep_entrega, 1.5 * cm, y)
        campo("Cidade/Estado", f"{pedido.cidade}/{pedido.estado}" if pedido.cidade else "—", 7 * cm, y)
        y -= 1 * cm
        campo("Rua", f"{pedido.rua}, {pedido.numero}" if pedido.rua else "—", 1.5 * cm, y)
        campo("Bairro", pedido.bairro or "—", 12 * cm, y)
        y -= 1 * cm
        if pedido.complemento:
            campo("Complemento", pedido.complemento, 1.5 * cm, y)
            y -= 1 * cm
    else:
        c.setFillColor(TEXT_LIGHT)
        c.setFont("Helvetica", 10)
        c.drawString(1.5 * cm, y, "Endereco nao informado")
        y -= 1 * cm

    # ==========================================
    # SEÇÃO: ITENS DO PEDIDO
    # ==========================================
    y -= 0.3 * cm
    y = secao_titulo("Itens do Pedido", y)
    y -= 0.3 * cm

    for i, item in enumerate(pedido.itens.all()):
        # Verifica se precisa de nova página
        if y < 5 * cm:
            c.showPage()
            y = height - 2 * cm

        # Card do item
        card_height = 2.5 * cm

        # Verifica personalizações para calcular altura
        opcoes_formatadas = []
        if item.opcoes:
            for chave, valor in item.opcoes.items():
                if chave == "personalizacao":
                    opcoes_formatadas.append(("Personalizacao", str(valor)))
                    continue
                try:
                    grupo = GrupoOpcao.objects.get(id=int(chave))
                    nome_grupo = grupo.nome
                except:
                    nome_grupo = chave.capitalize()

                if isinstance(valor, list):
                    nomes = []
                    for v in valor:
                        try:
                            opcao = Opcao.objects.get(id=int(v))
                            nomes.append(opcao.nome)
                        except:
                            nomes.append(str(v))
                    valor_final = ", ".join(nomes)
                else:
                    try:
                        opcao = Opcao.objects.get(id=int(valor))
                        valor_final = opcao.nome
                    except:
                        valor_final = str(valor)

                opcoes_formatadas.append((nome_grupo, valor_final))

        card_height = max(2.5 * cm, 1.8 * cm + len(opcoes_formatadas) * 0.5 * cm)

        # Fundo alternado
        bg = HexColor('#fdf6fa') if i % 2 == 0 else WHITE
        c.setFillColor(bg)
        c.roundRect(1.5 * cm, y - card_height, width - 3 * cm, card_height, 8, fill=1, stroke=0)

        # Borda esquerda colorida
        c.setFillColor(BABY_PINK if i % 2 == 0 else BABY_LILAC)
        c.rect(1.5 * cm, y - card_height, 0.25 * cm, card_height, fill=1, stroke=0)

        # Número do item
        c.setFillColor(LILAC)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(2.2 * cm, y - 0.5 * cm, f"#{i+1}")

        # Nome do produto
        c.setFillColor(TEXT_DARK)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(3 * cm, y - 0.5 * cm, item.produto.nome)

        # Quantidade e preço
        c.setFillColor(PINK)
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(width - 2 * cm, y - 0.5 * cm, f"R$ {item.subtotal:.2f}")

        c.setFillColor(TEXT_MID)
        c.setFont("Helvetica", 9)
        c.drawRightString(width - 2 * cm, y - 1 * cm, f"Qtd: {item.quantidade} x R$ {item.preco_unitario:.2f}")

        # Opções/personalizações
        op_y = y - 1.3 * cm
        for nome_grupo, valor_final in opcoes_formatadas:
            c.setFillColor(LILAC)
            c.setFont("Helvetica-Bold", 8)
            c.drawString(3 * cm, op_y, f"{nome_grupo}:")
            c.setFillColor(TEXT_DARK)
            c.setFont("Helvetica", 8)
            c.drawString(3 * cm + c.stringWidth(f"{nome_grupo}: ", "Helvetica-Bold", 8), op_y, valor_final)
            op_y -= 0.45 * cm

        y -= card_height + 0.3 * cm

    # ==========================================
    # SEÇÃO: TOTAIS
    # ==========================================
    if y < 5 * cm:
        c.showPage()
        y = height - 2 * cm

    y -= 0.3 * cm

    # Caixa de totais
    total_box_height = 3.5 * cm
    c.setFillColor(HexColor('#fdf0f6'))
    c.roundRect(width - 9 * cm, y - total_box_height, 7.5 * cm, total_box_height, 8, fill=1, stroke=0)
    c.setStrokeColor(BORDER)
    c.setLineWidth(1)
    c.roundRect(width - 9 * cm, y - total_box_height, 7.5 * cm, total_box_height, 8, fill=0, stroke=1)

    ty = y - 0.8 * cm
    total_produtos = sum(item.subtotal for item in pedido.itens.all())
    valor_frete = pedido.total - total_produtos

    c.setFillColor(TEXT_MID)
    c.setFont("Helvetica", 10)
    c.drawString(width - 8.5 * cm, ty, "Subtotal:")
    c.setFillColor(TEXT_DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(width - 2 * cm, ty, f"R$ {total_produtos:.2f}")

    ty -= 0.7 * cm
    c.setFillColor(TEXT_MID)
    c.setFont("Helvetica", 10)
    c.drawString(width - 8.5 * cm, ty, "Frete:")
    c.setFillColor(TEXT_DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(width - 2 * cm, ty, f"R$ {valor_frete:.2f}" if valor_frete > 0 else "A calcular")

    # Linha divisória
    ty -= 0.4 * cm
    c.setStrokeColor(BORDER)
    c.line(width - 8.5 * cm, ty, width - 2 * cm, ty)

    ty -= 0.5 * cm
    c.setFillColor(TEXT_DARK)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(width - 8.5 * cm, ty, "TOTAL:")
    c.setFillColor(PINK)
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(width - 2 * cm, ty, f"R$ {pedido.total:.2f}")

    # ==========================================
    # FOOTER
    # ==========================================
    c.setFillColor(BABY_LILAC)
    c.rect(0, 0, width, 1.5 * cm, fill=1, stroke=0)

    c.setFillColor(WHITE)
    c.setFont("Helvetica", 8)
    c.drawCentredString(width / 2, 0.7 * cm, "Mimos da Nick  |  Feito com carinho para voce  |  Documento gerado automaticamente")

    c.save()
    return response