FROM alpine:latest

RUN apk upgrade --update && apk add --no-cache python3 python3-dev 

RUN pip3 install --no-cache-dir datetime

WORKDIR /app

COPY ./planner.py /app
COPY ./output.txt /app

ENTRYPOINT ["python3","planner.py"]
