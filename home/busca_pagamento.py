import os

import requests
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv(
    "MERCADO_PAGO_ACCESS_TOKEN",
)
PAYMENT_CONNECT_TIMEOUT = float(os.getenv("MERCADO_PAGO_PAYMENT_CONNECT_TIMEOUT", "20.0"))
PAYMENT_READ_TIMEOUT = float(os.getenv("MERCADO_PAGO_PAYMENT_READ_TIMEOUT", "20.0"))
MERCADO_PAGO_PAYMENT_URL = "https://api.mercadopago.com/v1/payments/{payment_id}"

# Função para buscar o pagamento no Mercado Pago usando o SDK
def buscar_pagamento_mercado_pago(pagamento_id):
    if not pagamento_id:
        print("ID do pagamento não informado.")
        return None

    try:
        response = requests.get(
            MERCADO_PAGO_PAYMENT_URL.format(payment_id=pagamento_id),
            headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
            timeout=(PAYMENT_CONNECT_TIMEOUT, PAYMENT_READ_TIMEOUT),
        )

        # Verificar se a resposta foi bem-sucedida
        if response.status_code == 200:
            dados_pagamento = response.json()
                        
            # Buscar os itens do pagamento
            itens = dados_pagamento.get('additional_info', {}).get('items', [])
            # inf = dados_pagamento.get('metadata', {}).get('other_info', [])
            # carrinho_id = dados_pagamento.get('metadata', {}).get('carrinho_id')
            # evento_id = dados_pagamento.get('metadata', {}).get('evento_id')
            payment_type = dados_pagamento.get('payment_type_id')
            # print(f"Informações adicionais: {inf}")
            # print(f"Carrinho ID: {carrinho_id}, Evento ID: {evento_id}")
            
            x = []
            if itens:
                for item in itens:
                    item_title = item.get('title', 'Sem título')
                    x.append(item_title)
            else:
                print("Nenhum item encontrado na resposta.")
            
            # Retornar os dados do pagamento
            return {
                "id": dados_pagamento.get('id'),
                "status": dados_pagamento.get('status'),
                "valor": dados_pagamento.get('transaction_amount'),
                "usuario": dados_pagamento.get('external_reference'),
                "data": dados_pagamento.get('date_approved'),
                "items": x,
                # "evento": evento_id,  
                # "carrinho_id": carrinho_id,
                "payment_type": payment_type

            }
        else:
            try:
                mp_response = response.json()
            except ValueError:
                mp_response = response.text
            print(f"Erro ao buscar o pagamento: {response.status_code}, {mp_response}")
            return {
                "erro": True,
                "mp_status": response.status_code,
                "mp_response": mp_response,
            }
    
    except Exception as e:
        print(f"Ocorreu um erro: {str(e)}")
        return {
            "erro": True,
            "mp_status": "exception",
            "mp_response": str(e),
        }
