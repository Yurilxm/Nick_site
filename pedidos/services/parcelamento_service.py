import requests
from django.conf import settings


def obter_parcelas(valor, bandeira):
    url = "https://api.mercadopago.com/v1/payment_methods/installments"

    params = {
        "amount": valor,
        "payment_method_id": bandeira,
    }

    headers = {
        "Authorization": f"Bearer {settings.MERCADO_PAGO_ACCESS_TOKEN}"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        data = response.json()
    except Exception:
        return _parcelas_fallback(valor)

    if not data:
        return _parcelas_fallback(valor)

    parcelas = data[0].get("payer_costs", [])

    return [
        {
            "numero": p["installments"],           # chave que o JS usa
            "valor_parcela": p["installment_amount"],
            "valor_total": p["total_amount"],
        }
        for p in parcelas
    ]


def _parcelas_fallback(valor):
    """Retorna parcelas estáticas se a API falhar ou bandeira não reconhecida."""
    try:
        v = float(valor)
    except (ValueError, TypeError):
        v = 0

    opcoes = [1, 2, 3, 6, 12]
    return [
        {
            "numero": n,
            "valor_parcela": round(v / n, 2),
            "valor_total": v,
        }
        for n in opcoes
        if v > 0
    ]