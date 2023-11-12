FROM python:3.10

ENV DEPLOY 1

WORKDIR /opt/tmp

COPY . .

RUN apt-get update && \
    apt-get install -y jq && \
    rm -rf /var/lib/apt/lists/* && \
    pip install -r requirements.txt

EXPOSE 6666

CMD ["sh", "start.sh"]
