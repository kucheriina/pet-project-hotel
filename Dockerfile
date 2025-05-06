FROM python:3.12

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only main --no-root

COPY . .

CMD ["python", "myhotel/manage.py", "runserver", "0.0.0.0:8000"]