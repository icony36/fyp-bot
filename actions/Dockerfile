FROM rasa/rasa-sdk:3.6.2
WORKDIR /app
ENV GOOGLE_API_KEY=AIzaSyAEihM76eVmnqFnV6xDg4N590NDONtCLxQ
ENV SERVER_ENDPOINT=https://fyp-server-b4yk.onrender.com/
COPY ./requirements.txt ./
#copy everything in ./actions directory (your custom actions code) to /app/actions in container
COPY ./ /app/actions

USER root
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --verbose -r requirements.txt
RUN pip install -U python-dotenv
EXPOSE 5055
USER 1001