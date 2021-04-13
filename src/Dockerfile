# pull official base image
FROM python:3.8.5-slim-buster

# set work directory
WORKDIR /infra-job

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ Asia/Shanghai

# copy requirements file
COPY ./src/requirements.txt /infra-job/requirements.txt

# install dependencies
RUN set -eux \
    && pip install -r /infra-job/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/\
    && rm -rf /root/.cache/pip

# copy project
COPY ./src /infra-job

# run app
CMD ["python", "./app/main.py"]