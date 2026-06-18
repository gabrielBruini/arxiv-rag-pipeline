# arXiv RAG Pipeline

Pipeline de RAG (retrieval-augmented generation) sobre papers de Ciência da
Computação do arXiv. Monorepo com quatro pacotes:

| Pacote | Papel |
|---|---|
| `crawler` | Coleta papers via OAI-PMH do arXiv (roda no Airflow). |
| `ingestion` | Lê o JSON do crawler, gera embeddings e indexa no Qdrant. |
| `rag` | API FastAPI que responde perguntas com base nos papers indexados. |
| `shared` | Entidades de domínio compartilhadas (ex.: `Paper`). |

## Configuração (`.env`)

Toda a configuração externa fica num único `.env` na raiz do projeto, lido por
todos os componentes via `python-dotenv`. Para começar:

```bash
cp .env.example .env   # ajuste os valores conforme o ambiente
```

Variáveis já presentes no ambiente têm precedência sobre o arquivo, e os valores
abaixo são os defaults usados quando nada é definido.

### Variáveis

| Variável | Default | Usada por | Descrição |
|---|---|---|---|
| `QDRANT_HOST` | `localhost` | ingestion, rag | Host do Qdrant. |
| `QDRANT_PORT` | `6333` | ingestion, rag | Porta HTTP do Qdrant. |
| `QDRANT_COLLECTION` | `arxiv_cs_papers` | ingestion, rag | Nome da collection. |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | ingestion, rag | Modelo do sentence-transformers. |
| `EMBEDDING_DEVICE` | *(vazio)* | ingestion, rag | Device do modelo. Vazio = autodetecta. Ex.: `cpu`, `cuda`. |
| `OLLAMA_MODEL` | `llama3.1` | rag | Modelo do Ollama usado para gerar respostas. |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | rag | URL do servidor Ollama. |
| `RAG_TOP_K` | `5` | rag | Quantidade de papers recuperados por consulta. |
| `INGEST_BATCH_SIZE` | `64` | ingestion | Tamanho do lote de embedding/upsert. |
| `ARXIV_OAI_BASE_URL` | `https://oaipmh.arxiv.org/oai` | crawler | Endpoint OAI-PMH do arXiv. |
| `ARXIV_METADATA_PREFIX` | `arXiv` | crawler | Formato de metadados do OAI-PMH. |
| `ARXIV_SET_SPEC` | `cs` | crawler | Set do arXiv a coletar (`cs` = Ciência da Computação). |
| `ARXIV_REQUEST_DELAY` | `3` | crawler | Segundos entre requisições (rate limit). |
| `HTTP_TIMEOUT` | `120` | crawler | Timeout das requisições HTTP, em segundos. |
| `HTTP_CHUNK_SIZE` | `8192` | crawler | Tamanho do chunk de download, em bytes. |

> No Airflow (Docker), o crawler recebe as variáveis `ARXIV_*`/`HTTP_*` pelo
> `environment` do `docker-compose.yml`, que as interpola a partir do `.env` da
> raiz com fallback para os defaults.

## Como rodar

```bash
# 1. Sobe Qdrant + Airflow (e Postgres)
docker compose up -d

# 2. Crawler: dispare a DAG `arxiv_harvester` na UI do Airflow (http://localhost:8080)
#    ou rode a ingestion a partir de um JSON já coletado:
python ingestion/main_ingest.py

# 3. API de RAG
uvicorn rag.main:app --reload --port 8000
# docs interativas em http://localhost:8000/docs
```

Pré-requisitos para respostas reais: Qdrant populado (via crawler + ingestion) e
um servidor Ollama com o modelo configurado (`ollama pull llama3.1`).
