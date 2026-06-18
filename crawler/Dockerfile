FROM apache/airflow:2.9.0-python3.12

COPY crawler/requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

COPY --chown=airflow:root shared /shared
RUN pip install --no-cache-dir -e /shared

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY --chown=airflow:root ingestion /ingestion
RUN pip install --no-cache-dir -e /ingestion
