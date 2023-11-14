FROM python:3.10

RUN apt -y update
RUN apt -y upgrade

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./bot.py" ]

