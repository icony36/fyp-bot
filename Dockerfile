FROM rasa/rasa:3.6.2
WORKDIR /app
COPY . /app
USER root
COPY ./data /app/data
RUN  rasa train
VOLUME /app
VOLUME /app/data
VOLUME /app/models
# CMD ["run","--ssl-certificate","/etc/letsencrypt/live/iantan.site/fullchain.pem","--ssl-keyfile","/etc/letsencrypt/live/iantan.site/privkey.pem","-m","/app/models","--enable-api","--cors","*","--debug" ,"--endpoints", "endpoints.yml", "--log-file", "out.log", "--debug"]

CMD [ "run","-m","/app/models","--enable-api","--cors","*","--debug","--endpoints","endpoints.yml"]