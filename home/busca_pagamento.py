import mercadopago
import os
from dotenv import load_dotenv

load_dotenv()
# Substitua pelo seu token de acesso do Mercado Pago
ACCESS_TOKEN = "TEST-3488797328851277-091614-dbbff0af2658e101ee7f9413497c16fd-162016798"

# Inicializar o SDK do Mercado Pago
sdk = mercadopago.SDK(ACCESS_TOKEN)

# Função para buscar o pagamento no Mercado Pago usando o SDK
def buscar_pagamento_mercado_pago(pagamento_id):
    try:
        # Usando o SDK para buscar o pagamento
        pagamento = sdk.payment().get(pagamento_id)

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
    
    except Exception as e:
        print(f"Ocorreu um erro: {str(e)}")