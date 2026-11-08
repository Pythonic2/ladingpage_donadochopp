# GCS no Raspberry

## Problema e objetivo

O Cloud Run usa o bucket privado `gesttechmidias`, mas o Compose do Raspberry
ainda configura o filesystem local como fonte de mídia. O objetivo é fazer o
container do Raspberry usar o mesmo backend GCS e o prefixo isolado
`landing-page-ddc/midias/`, sem versionar ou duplicar credenciais.

## Fatos observados

- O backend Django para GCS, URLs assinadas e uploads sem sobrescrita já existe.
- As dependências `django-storages` e `google-cloud-storage` já estão instaladas.
- O projeto de referência monta uma credencial externa em
  `/run/secrets/gcp.json`, somente leitura.
- A política de infraestrutura permite reutilizar essa credencial entre projetos
  autorizados.

## Regras e premissas

- O bucket continua privado.
- O prefixo da aplicação é fixo e separado dos demais projetos.
- A chave JSON permanece fora do Git e da imagem.
- A conta da chave já deve ter acesso mínimo necessário ao bucket.
- Nenhum objeto existente será copiado, sobrescrito ou excluído nesta mudança.

## Cenários

### Inicialização com credencial

Dado que a credencial autorizada existe no host Raspberry, quando o Compose
iniciar o serviço, então o arquivo deve aparecer somente para leitura em
`/run/secrets/gcp.json` e o Django deve selecionar o backend GCS.

### Isolamento de mídia

Dado que o backend GCS está ativo, quando uma mídia for salva, então seu objeto
deve ficar sob `landing-page-ddc/midias/`, sem sobrescrever um nome existente.

### Falha segura

Dado que a credencial esteja ausente ou sem permissão, quando o storage for
acessado, então a operação deve falhar sem recorrer silenciosamente ao volume
local e sem expor o segredo em logs.

## Critérios de aceitação e verificações

1. O Compose resolve sem erros (`docker compose config --quiet`).
2. `GCS_ENABLED=true`, `SERVE_MEDIA=false` e o prefixo correto chegam ao serviço
   (inspeção da configuração resolvida, sem valores secretos).
3. A credencial externa é montada em modo `ro` no caminho esperado (inspeção da
   configuração resolvida).
4. Os testes Django de storage e o `manage.py check` passam.
5. No Raspberry, uma leitura e um upload controlado confirmam o acesso real ao
   GCS; essa verificação externa não faz parte da alteração local.

## Fora de escopo

- Criar ou rotacionar credenciais e permissões IAM.
- Sincronizar mídias locais, alterar DNS/Cloudflare ou fazer deploy.
- Executar migrations ou modificar dados de produção.

## Segurança e recuperação

O limite de confiança fica entre o host Raspberry, o container e o GCS. A chave
é somente leitura no filesystem do container, mas a identidade pode gravar
objetos conforme seu IAM. O rollback consiste em reverter a configuração do
Compose; isso não altera nem remove objetos do bucket ou o volume local.
