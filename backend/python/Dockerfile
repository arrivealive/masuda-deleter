FROM python:3.11.0
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/

#chrome
RUN apt-get autoclean
RUN apt-get clean all
RUN apt-get update
# chromium >=107.0.5304.87
RUN apt-get install -y chromium chromium-driver 
#nodejs, npm
# RUN apt-get install -y nodejs npm
