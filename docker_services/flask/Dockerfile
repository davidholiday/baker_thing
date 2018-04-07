FROM ubuntu:latest
MAINTAINER David Holiday


RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
RUN pip install flask flask_sqlalchemy sqlalchemy_utils psycopg2
CMD ["python", "/opt/flask_app_source/app.py"]
