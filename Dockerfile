# develop image contains the dependencies and no application code
FROM python:3.10 as develop

RUN apt -y update
RUN apt -y upgrade

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD ["/usr/bin/tail", "-f"]



# prod image inherits from develop and adds application code
FROM develop as prod

WORKDIR /usr/src/app

COPY . .

CMD [ "python", "./bot.py" ]
