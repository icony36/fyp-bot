FROM rasa/rasa:3.6.2
WORKDIR /app
COPY . /app
USER root
# WORKDIR /app
# COPY . /app
COPY ./data /app/data
RUN  rasa train
VOLUME /app
VOLUME /app/data
VOLUME /app/models
CMD ["run","-m","/app/models","--enable-api","--cors","*","--debug" ,"--endpoints", "endpoints.yml", "--log-file", "out.log", "--debug"]

# FROM python:3.9.13 AS BASE

# RUN apt-get update \
#     && apt-get --assume-yes --no-install-recommends install \
#         build-essential \
#         curl \
#         git \
#         jq \
#         libgomp1 \
#         vim

# WORKDIR /app

# # upgrade pip version
# RUN pip install --no-cache-dir --upgrade pip

# RUN pip install rasa==3.6.12

# ADD config.yml config.yml
# ADD domain.yml domain.yml
# ADD credentials.yml credentials.yml
# ADD endpoints.yml endpoints.yml