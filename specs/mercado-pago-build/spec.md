# Inicialização segura do Mercado Pago no build

## Objetivo

Permitir que comandos de build do Django, como `collectstatic`, carreguem as URLs sem exigir a credencial do Mercado Pago. A credencial deve ser lida somente ao criar uma preferência de pagamento.

## Cenários e critérios de aceitação

- Sem `MERCADO_PAGO_ACCESS_TOKEN`, importar a aplicação e executar `collectstatic` não inicializa o SDK nem falha.
- Ao tentar criar uma preferência sem a variável, nenhuma chamada ao SDK ou à API externa é feita e a função preserva o contrato atual de retornar `None` em caso de erro.
- Com a variável presente, o SDK recebe o token em memória e a resposta bem-sucedida mantém o formato atual.
- Nenhum valor de credencial é incluído no código, testes, imagem Docker ou Git.

## Matriz de testes

| Caso | Evidência esperada |
| --- | --- |
| Preferência sem token | SDK não chamado; retorno `None` |
| Preferência com token de teste | SDK chamado uma vez; resposta preservada |
| Build sem `.env` na imagem | `collectstatic` e build Docker concluídos |
| Regressão Django | Suite `home` e `manage.py check` aprovados |

## Falhas e recuperação

Se a credencial estiver ausente em runtime, a criação da preferência falha de forma controlada, sem chamada externa. A reversão consiste em restaurar a inicialização anterior, mas isso reintroduz a falha durante o build e não é recomendado.
