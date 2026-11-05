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

Os padrões são serviço `landingpage-donadochopp` e região `europe-west1`. Para
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

## Arquivos de mídia

WhiteNoise serve os arquivos estáticos empacotados na imagem. Uploads em
`MEDIA_ROOT` são efêmeros no Cloud Run; para uploads persistentes, configure
Google Cloud Storage ou outro armazenamento de objetos antes de colocar essa
função em produção.

