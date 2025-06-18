FROM agrigorev/zoomcamp-model:mlops-2024-3.10.13-slim

RUN pip install -U pip
RUN pip install pipenv

WORKDIR /app

RUN ["mkdir", "-p", "/app/output" ]

COPY ["Pipfile", "Pipfile.lock", "./"]

RUN pipenv install --deploy --system 

COPY [ "starter.py" , "./"]

CMD ["python", "starter.py", "2023", "5"]
