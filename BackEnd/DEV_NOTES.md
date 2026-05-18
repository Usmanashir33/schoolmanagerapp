# 📘 School Project Dev Guide (Docker + Django + Celery)

## 1. System Architecture

Django → Celery → Redis → Background Tasks

------------------------------------------------------------------------

## 2. Redis (Docker)

### First time only

docker run -d --name redis -p 6379:6379 redis

### Start later

docker start redis

### Stop

docker stop redis

### Restart

docker restart redis

### Check

docker ps docker ps -a

------------------------------------------------------------------------

## 3. Django Server

python manage.py runserver

------------------------------------------------------------------------

## 4. Celery Worker

celery -A SchoolManagerProj worker --loglevel=info

Recommended: celery -A SchoolManagerProj worker --loglevel=info
--concurrency=1

------------------------------------------------------------------------

## 5. Full Dev Workflow

If Redis exists: docker start redis python manage.py runserver celery -A
SchoolManagerProj worker --loglevel=info

If Redis not created: docker run -d --name redis -p 6379:6379 redis
python manage.py runserver celery -A SchoolManagerProj worker
--loglevel=info

------------------------------------------------------------------------

## 6. Docker Commands

docker images docker rmi redis

docker ps docker ps -a docker rm `<id>`{=html}

docker run redis

------------------------------------------------------------------------

## 7. Docker Compose

### Example

version: "3.9"

services: redis: image: redis ports: - "6379:6379"

django: build: . command: python manage.py runserver 0.0.0.0:8001
ports: - "8000:8000" depends_on: - redis

celery: build: . command: celery -A SchoolManagerProj worker
--loglevel=info depends_on: - redis

### check celery log error 
celery -A SchoolManagerProj worker -l info -E

## on windows for same and avaoid multiple 
celery -A SchoolManagerProj worker --loglevel=info --pool=solo --concurrency=1
celery -A SchoolManagerProj worker --loglevel=info --pool=solo --concurrency=1

------------------------------------------------------------------------

## Run everything

docker-compose up

## Stop everything

docker-compose down

------------------------------------------------------------------------

## 8. Key Idea

Docker = services Redis = broker Celery = worker Django = API Compose =
automation


## 9 docker-decompose file  SAMPLE 

services:
  redis:
    image: redis
    ports:
      - "6379:6379"

  django:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - redis

  celery:
    build: .
    command: celery -A SchoolManagerProj worker --loglevel=info
    depends_on:
      - redis

<!-- Dockerfile sample  -->
FROM python:3.12

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt


## both docker-compose and Dockerfile must be  stored in same project root with manage.py file ..

In normal english 
docker is the engine that has redis container 

we need redis container,celery,django app  thats why we need docker here . 
it can hold all the containers above  and run it in one container  with disfferent container names , 


docker-compose  file  
'docker-compose up'   # to start the docker server so that all the commands inside it will start.

in the first time we nee d 'docker-compose up --build' so that it combine the containers and prepare it in the first time .

we also need Dockerfile to tell the compose this is our djnago projects data to build its required by docker ,
 it also has .dockerignor  for the files need not to be composed togetther 