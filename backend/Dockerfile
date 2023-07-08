FROM python:3.9-slim
COPY ./conf/ .
RUN pip3 install -r ./requirements.txt --no-cache-dir
CMD ["gunicorn", "conf.wsgi:application", "--bind", "0:8000" ]