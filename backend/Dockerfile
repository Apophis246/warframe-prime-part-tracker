# Dockerfile — outline only, no implementation yet.
#
# Builds the backend into an image that runs uvicorn serving the FastAPI
# app. Single-stage is fine here (unlike the frontend) — there's no
# separate "build" step, Python just runs.

FROM python:3.12-slim

WORKDIR /code

COPY ./requirements.txt ./
RUN pip install -r requirements.txt

COPY ./app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

