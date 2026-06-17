# gov-shared

Código compartilhado entre os projetos do `gov-rag-pipeline` (crawler, ingestion).

Contém entidades de domínio comuns, como `Paper`.

## Instalação

Em modo editável (desenvolvimento), a partir da raiz de cada projeto:

```bash
pip install -e ../shared
```

## Uso

```python
from shared.entities.paper import Paper
```

## Namespace package

O pacote `shared` é um *namespace package* (PEP 420), sem `__init__.py`.
Assim ele se funde com o `shared` interno de cada projeto — por exemplo,
no crawler convivem `shared.config`/`shared.logger` (locais) e
`shared.entities.paper` (deste pacote).