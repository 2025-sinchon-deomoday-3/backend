FROM python:3.8.3-alpine
ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app

# dependencies for psycopg2-binary
RUN apk add --no-cache mariadb-connector-c-dev
RUN apk update && apk add python3 python3-dev mariadb-dev build-base && pip3 install mysqlclient==2.2.4 && apk del python3-dev mariadb-dev build-base


# By copying over requirements first, we make sure that Docker will cache
# our installed requirements rather than reinstall them on every build
RUN apk update && apk add libpq
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add --no-cache jpeg-dev zlib-dev mariadb-dev
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
RUN apk del jpeg-dev zlib-dev

# Now copy in our code, and run it
COPY . /app/