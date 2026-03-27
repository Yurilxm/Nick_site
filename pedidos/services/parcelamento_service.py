import requests
from django.conf import settings


def obter_parcelas(valor, bandeira):
    """
    Retorna lista de opções de parcelamento.
    Inclui campo 'sem_juros' para uso no frontend.
    """
    try:
        valor = float(valor)
    except (ValueError, TypeError):
        valor = 0

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
    if not parcelas:
        return _parcelas_fallback(valor)

    return [
        {
            "numero": p["installments"],
            "valor_parcela": p["installment_amount"],
            "valor_total": p["total_amount"],
            "sem_juros": p.get("installment_rate", 1) == 0,
        }
        for p in parcelas
    ]


def _parcelas_fallback(valor):
    """
    Retorna parcelas padrão caso a API não retorne.
    1x e 2x são sempre sem juros.
    """
    try:
        v = float(valor)
    except (ValueError, TypeError):
        v = 0

    opcoes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    resultado = []
    for n in opcoes:
        valor_parcela = v if n == 1 else round(v / n, 2)
        resultado.append({
            "numero": n,
            "valor_parcela": valor_parcela,
            "valor_total": v,
            "sem_juros": n <= 2,
        })
    return resultado