FROM python:3.12

WORKDIR /app

COPY . /app
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0

RUN pip install --upgrade pip
# RUN pip install -r requirements.txt
RUN pip install Django==5.1.4 celery ==5.5.3
