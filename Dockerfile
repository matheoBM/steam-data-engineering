FROM apache/airflow:2.8.1-python3.11

USER root

# Copy everything needed for install
COPY . /app

WORKDIR /app

# Set permissions so 'airflow' user can write
RUN chown -R airflow: /app

# Make your project available to Airflow
ENV PYTHONPATH="${PYTHONPATH}:/app"


USER airflow

# Install your custom project in editable mode using constraint file
RUN pip install --no-cache-dir -e . -c constraints.txt