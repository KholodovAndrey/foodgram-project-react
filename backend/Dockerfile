FROM python:3.9-slim
WORKDIR /app
COPY ./conf/requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir
COPY ./conf/ .
CMD ["gunicorn", "conf.wsgi:application", "--bind", "0:8000" ]