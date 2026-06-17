FROM apache/airflow:2.9.0-python3.12

# Dependências do crawler
COPY crawler/requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Pacote compartilhado (entidades de domínio comuns), instalado em modo editável.
# O conteúdo de /shared é sobreposto por um volume em runtime (ver docker-compose.yml),
# então edições no host refletem no container sem rebuild.
COPY shared /shared
RUN pip install --no-cache-dir -e /shared
