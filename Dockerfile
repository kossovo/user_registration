FROM python:3.9

LABEL maintainer = Clovis NZOUENDJOU <nzouendjou2002@yahoo.fr>
ENV VERSION = 1.0.1

ENV PYTHONUNBUFFERED=1
WORKDIR /app
RUN mkdir alembic

COPY requirements.txt ./requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
COPY . /app
EXPOSE 8000
