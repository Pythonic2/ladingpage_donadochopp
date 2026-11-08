# Plano

1. Documentar o comportamento e os limites de segurança.
2. Configurar no Compose o backend GCS e a credencial externa somente leitura.
3. Documentar os pré-requisitos e a validação no Raspberry.
4. Validar Compose, Django e testes de storage localmente.
5. Revisar o diff para evitar segredos, permissões excessivas e alterações fora
   do escopo.

## Matriz de testes

| Critério | Verificação | Ambiente |
|---|---|---|
| Compose válido | `docker compose config --quiet` | Local |
| Backend e prefixo | inspeção sanitizada de `docker compose config` | Local |
| Mount somente leitura | inspeção sanitizada de `docker compose config` | Local |
| Configuração Django | `python manage.py check` | Local |
| Storage e URLs | testes de `home` | Local, com mocks |
| Acesso real ao bucket | leitura e upload controlado | Raspberry, pendente de autorização operacional |

## Riscos

- A credencial pode não existir no caminho do host ou não ter IAM suficiente.
- Containers com acesso ao arquivo montado herdam o alcance da identidade.
- Mídias que existam apenas no volume local não aparecem no GCS até uma
  sincronização separada e explicitamente autorizada.
