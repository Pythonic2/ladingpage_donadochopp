import os

import mercadopago
from mercadopago.config import RequestOptions
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv(
    "MERCADO_PAGO_ACCESS_TOKEN",
)
sdk = mercadopago.SDK(ACCESS_TOKEN)
request_options = RequestOptions(
    connection_timeout=float(os.getenv("MERCADO_PAGO_PAYMENT_TIMEOUT", "8.0")),
    max_retries=int(os.getenv("MERCADO_PAGO_PAYMENT_RETRIES", "1")),
)

# Função para buscar o pagamento no Mercado Pago usando o SDK
def buscar_pagamento_mercado_pago(pagamento_id):
    if not pagamento_id:
        print("ID do pagamento não informado.")
        return None

    try:
        # Usando o SDK para buscar o pagamento
        pagamento = sdk.payment().get(pagamento_id, request_options=request_options)

        # Verificar se a resposta foi bem-sucedida
        if pagamento["status"] == 200:
            dados_pagamento = pagamento["response"]
                        
            # Buscar os itens do pagamento
            itens = dados_pagamento.get('additional_info', {}).get('items', [])
            # inf = dados_pagamento.get('metadata', {}).get('other_info', [])
            # carrinho_id = dados_pagamento.get('metadata', {}).get('carrinho_id')
            # evento_id = dados_pagamento.get('metadata', {}).get('evento_id')
            payment_type = pagamento['response']['payment_type_id']
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
            print(f"Erro ao buscar o pagamento: {pagamento['status']}, {pagamento['response']}")
            return {
                "erro": True,
                "mp_status": pagamento.get("status"),
                "mp_response": pagamento.get("response"),
            }
    
    except Exception as e:
        print(f"Ocorreu um erro: {str(e)}")
        return {
            "erro": True,
            "mp_status": "exception",
            "mp_response": str(e),
        }
