import requests
from django.conf import settings


def calcular_frete_melhor_envio(cep_destino, itens):
    url = "https://sandbox.melhorenvio.com.br/api/v2/me/shipment/calculate"

    headers = {
        "Authorization": f"Bearer {settings.MELHOR_ENVIO_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "MimosNick contato@mimosnick.com.br",
    }

    produtos = []
    for item in itens:
        produtos.append({
            "id": str(item.produto.id),
            "width": float(item.produto.largura),
            "height": float(item.produto.altura),
            "length": float(item.produto.comprimento),
            "weight": float(item.produto.peso),
            "insurance_value": float(item.preco_unitario),
            "quantity": item.quantidade,
        })

    payload = {
        "from": {"postal_code": settings.CEP_LOJA},
        "to": {"postal_code": cep_destino},
        "products": produtos,
        "options": {
            "receipt": False,
            "own_hand": False,
        },
        "services": ""
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        data = response.json()
    except Exception as e:
        return []

    opcoes = []
    for servico in data:
        if isinstance(servico, dict) and not servico.get("error"):
            opcoes.append({
                "id": servico.get("id"),
                "nome": servico.get("name"),
                "transportadora": servico.get("company", {}).get("name"),
                "preco": servico.get("price"),
                "prazo": servico.get("delivery_time"),
            })

    return sorted(opcoes, key=lambda x: float(x["preco"] or 999))