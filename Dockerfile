FROM debian:buster

EXPOSE 5000

# Create the working directory
RUN mkdir -p /usr/src/app

# Set the working directory
WORKDIR /usr/src/app

# Copy the folder content to the working directory
COPY . /usr/src/app

RUN apt-get update
RUN apt-get -y install gnupg2 && apt-get -y install curl && curl -s https://packagecloud.io/install/repositories/tokbox/debian/script.deb.sh | bash && apt-get -y install libopentok-dev
RUN apt-get -y install build-essential cmake clang libc++-dev libc++abi-dev pkg-config libasound2 libpulse-dev libsdl2-dev && mkdir src/build && cd src/build && CC=clang CXX=clang++ cmake ..
RUN apt-get -y install libcairo2-dev libjpeg-dev libgif-dev
RUN apt-get -y install libcurl4-openssl-dev libssl-dev
RUN apt-get -y install unattended-upgrades
RUN apt-get -y install protobuf-compiler
RUN apt-get -y install python3.7 && apt-get -y install python3-pip && pip3 install --upgrade pip
RUN pip config set global.extra-index-url "https://artifactory.vgcva0.prod.vonagenetworks.net/artifactory/api/pypi/python-local-ai/simple"

RUN python3.7 -m pip install -r requirements.txt
RUN pip install overai-speech

# Create build directory and navigate inside
RUN cd src/build && make

CMD ["python3.7", "src/server.py"]