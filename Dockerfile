FROM python:3.9.13
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /code
RUN pip install --upgrade pip
COPY ./requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt
COPY . /code/
RUN apt-get update && apt-get install -y nginx
RUN rm /etc/nginx/sites-enabled/default
COPY ./nginx.conf /etc/nginx/sites-enabled/
EXPOSE 80 443
CMD service nginx start && gunicorn myproject.wsgi.application --bind
0.0.0.0:8000