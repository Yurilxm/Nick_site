import requests
from django.conf import settings


def obter_parcelas(valor, bandeira):

    url = "https://api.mercadopago.com/v1/payment_methods/installments"

    params = {
        "amount": valor,
        "payment_method_id": bandeira
    }

    headers = {
        "Authorization": f"Bearer {settings.MERCADOPAGO_ACCESS_TOKEN}"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers
    )

    data = response.json()

    if not data:
        return []

    parcelas = data[0]["payer_costs"]

    resultado = []

    for p in parcelas:

        resultado.append({
            "parcelas": p["installments"],
            "valor_parcela": p["installment_amount"],
            "valor_total": p["total_amount"]
        })

    return resultado