FROM python:3.12-alpine
WORKDIR src/
COPY ../Pipfile ../Pipfile.lock ./
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir pipenv && pipenv install --dev --system --deploy
COPY ../src/ ./
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8100"]
