FROM python:3-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/

ENV APP_HOME=/code 
WORKDIR $APP_HOME 
COPY requirements.txt $APP_HOME/ 

RUN  pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . $APP_HOME/
COPY entrypoint.sh $APP_HOME/
RUN chmod +x  $APP_HOME/entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["sh", "/code/entrypoint.sh"]