# Deploy no Google Cloud Run

O projeto está preparado para usar o mesmo PostgreSQL configurado no
`comercial_tool`, isolado pelo schema `ladingpageddc`.

## Pré-requisitos

- Google Cloud CLI instalada e autenticada (`gcloud auth login`)
- projeto selecionado (`gcloud config set project ID_DO_PROJETO`)
- `.env` desta aplicação com as variáveis do Mercado Pago
- `../comercial_tool/.env` com as credenciais do PostgreSQL

O script lê os dois arquivos, gera uma configuração temporária fora do projeto,
força `DB_SCHEMA=ladingpageddc` e apaga o temporário ao terminar. Os arquivos
`.env` não entram na imagem Docker.

## Deploy

```bash
chmod +x deploy-cloud-run.sh
./deploy-cloud-run.sh
```

Os padrões são serviço `landingpage-donadochopp` e região `southamerica-east1`. Para
alterá-los:

```bash
SERVICE=meu-servico REGION=southamerica-east1 ./deploy-cloud-run.sh
```

## Migrações

O servidor não cria migrations nem altera o banco automaticamente. Antes do
primeiro deploy, crie o schema e aplique as migrations com:

```bash
chmod +x migrate-production.sh
./migrate-production.sh
```

Esse comando altera o PostgreSQL configurado no `comercial_tool`, mas somente
dentro do schema `ladingpageddc`. Em uma esteira automatizada, prefira executar
essa etapa em um Cloud Run Job. `RUN_MIGRATIONS=true` existe apenas para uma
execução controlada; mantenha-o como `false` no serviço web.

## Arquivos de mídia no Google Cloud Storage

WhiteNoise continua atendendo somente os arquivos estáticos. Com
`GCS_ENABLED=true`, todos os `FileField` e `ImageField` usam o bucket privado
`gesttechmidias` via Application Default Credentials (ADC), sem chave JSON.

As mídias desta aplicação ficam sob o prefixo:

```text
gs://gesttechmidias/landing-page-ddc/midias/
```

Variáveis necessárias:

```env
GCS_ENABLED=true
GCS_BUCKET_NAME=gesttechmidias
GCS_PROJECT_ID=gestcloud-500200
GCS_APP_PREFIX=landing-page-ddc
GCS_SIGNED_URL_TTL=900
GCS_IAM_SIGN_BLOB=true
GCS_SA_EMAIL=926822874156-compute@developer.gserviceaccount.com
MEDIA_MAX_UPLOAD_SIZE=26214400
```

O bucket permanece privado. O backend gera URLs assinadas temporárias; o
prefixo da aplicação é definido por variável de ambiente do servidor e nunca
por dados enviados pelo frontend.

### IAM

A conta do Cloud Run precisa de `roles/storage.objectUser` no bucket. Para
assinar URLs usando ADC sem chave privada, ela também precisa da permissão
`iam.serviceAccounts.signBlob`, normalmente concedida com
`roles/iam.serviceAccountTokenCreator` **sobre a própria conta de serviço**.
Nenhuma permissão IAM é alterada pelos scripts deste repositório.

### Migrar as mídias locais

O comando abaixo apenas mostra o plano e não altera o bucket:

```bash
GCS_ENABLED=true venv/bin/python manage.py sync_media_to_gcs
```

Depois de revisar, faça a cópia sem sobrescrever nem excluir objetos:

```bash
GCS_ENABLED=true venv/bin/python manage.py sync_media_to_gcs --execute
```

Execute com ADC local (`gcloud auth application-default login`) ou no Cloud Run.
Os caminhos existentes do banco são preservados sob o prefixo da aplicação.

### Teste de integração controlado

Com ADC e as variáveis acima configuradas, envie um arquivo de teste pelo admin,
confirme que o objeto foi criado sob `landing-page-ddc/midias/` e abra a página
que o referencia. A URL deve conter assinatura e expirar após o TTL definido.
Exclua o objeto de teste pelo admin ao terminar; não torne o bucket público.

## Raspberry Pi com Docker Compose

No Raspberry, o Compose ativa o mesmo backend GCS e o mesmo prefixo usados no
Cloud Run. A credencial permanece fora do repositório e é montada somente para
leitura em `/run/secrets/gcp.json`:

```text
/home/pi/gcp-secrets/eventos-ddc.json
```

Essa credencial pode ser reutilizada somente enquanto a conta de serviço tiver
autorização para o prefixo desta aplicação no bucket privado. O arquivo não deve
ser copiado para o repositório nem para a imagem Docker.

Antes de subir o serviço, valide no próprio Raspberry:

```bash
test -r /home/pi/gcp-secrets/eventos-ddc.json
docker compose config --quiet
docker compose up -d --build
```

Depois, confirme que o container enxerga a configuração sem imprimir o conteúdo
da credencial, que uma mídia existente é carregada e que um novo upload é salvo
sob `landing-page-ddc/midias/`. O volume local `/app/media` é mantido apenas para
compatibilidade e recuperação; com `GCS_ENABLED=true`, ele não é a fonte
principal das mídias.

