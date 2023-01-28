FROM python:3.10-buster

ADD . ./app

WORKDIR /app

RUN pip install -r ./requirements.txt

EXPOSE 8000

CMD ["./start_server.sh"]