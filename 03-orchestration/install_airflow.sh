# find the right constraints URL at https://airflow.apache.org/docs/apache-airflow/stable/installation/installing-from-pypi.html
AIRFLOW_VERSION=3.0.1
PYTHON_VERSION="$(python3 --version | cut -d' ' -f2 | cut -d. -f1-2)"
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"

