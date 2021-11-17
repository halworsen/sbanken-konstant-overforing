FROM alpine:3.14.0

RUN apk upgrade
RUN apk add --no-cache python3
RUN apk add --no-cache py3-pip

RUN addgroup -S sbko
RUN adduser -h /home/sbko -s /bin/sh -D -u 1000 sbko sbko -G sbko
WORKDIR /home/sbko

COPY ./src/ .
COPY ./requirements.txt .
RUN pip install -r requirements.txt

CMD [ "python3", "./main.py" ]
