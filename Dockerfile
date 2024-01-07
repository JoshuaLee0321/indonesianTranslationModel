FROM python:3.8
WORKDIR /app
ADD . /app/
# this line is important to build dependence
RUN mkdir translation_file

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN pip3 install ckiptagger

RUN apt update

ENTRYPOINT python3 app.py
