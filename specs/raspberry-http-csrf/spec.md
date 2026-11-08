# Login via HTTP na rede local

## Objetivo

Permitir autenticação e formulários protegidos por CSRF quando a aplicação do Raspberry for acessada diretamente por `http://192.168.0.6:8010`, sem enfraquecer os padrões de ambientes HTTPS.

## Critérios de aceitação

- Em produção sem overrides, cookies de sessão e CSRF continuam marcados como Secure.
- O Compose do Raspberry pode desativar essas flags explicitamente para acesso HTTP local.
- A proteção CSRF permanece ativa; somente o atributo Secure dos cookies é configurável.
- Cloud Run e outros ambientes que não usam o Compose mantêm os padrões seguros.

## Matriz de testes

| Cenário | Resultado esperado |
| --- | --- |
| Produção sem overrides | `SESSION_COOKIE_SECURE=True` e `CSRF_COOKIE_SECURE=True` |
| Produção com overrides `false` | Ambas as flags ficam `False` |
| Verificação Django | Nenhum erro de configuração |
| Suite da aplicação | Sem regressões |

## Risco e recuperação

Cookies sem o atributo Secure podem trafegar por HTTP. Esta exceção deve ficar restrita à LAN confiável. Para publicar o serviço somente em HTTPS, remova os overrides ou configure ambos como `true` e mantenha `DJANGO_SECURE_SSL_REDIRECT=true`.
