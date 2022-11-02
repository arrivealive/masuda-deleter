FROM python:3.11.0
# FROM python:3.10.0
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
# list installable versions
# apt-cache showpkg chromium 
#chromium 107.0.5304.87
# RUN apt-get install -y chromium chromium-driver 
RUN apt-get install -y chromium=107.0.5304.87-1~deb11u1
RUN apt-get install -y chromium-driver=107.0.5304.87-1~deb11u1
# RUN apt-get install -y fonts-ipafont-gothic fonts-ipafont-mincho
#nodejs, npm
# RUN apt-get install -y nodejs npm
