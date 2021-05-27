FROM debian:buster

# Create the working directory
RUN mkdir -p /usr/src/app

# Set the working directory
WORKDIR /usr/src/app

# Copy the folder content to the working directory
COPY . /usr/src/app

RUN apt-get update
RUN apt-get -y install gnupg2 && apt-get -y install wget && echo "deb https://dl.bintray.com/tokbox/debian buster main" | tee -a /etc/apt/sources.list && wget -O- -q https://bintray.com/user/downloadSubjectPublicKey?username=bintray | apt-key add - && apt-get update && apt-get -y install libopentok-dev
RUN apt-get -y install build-essential cmake clang libc++-dev libc++abi-dev pkg-config libasound2 libpulse-dev libsdl2-dev && mkdir src/build && cd src/build && CC=clang CXX=clang++ cmake ..
RUN apt-get -y install libcairo2-dev libjpeg-dev libgif-dev
RUN apt-get -y  install libcurl4-openssl-dev libssl-dev
RUN apt-get -y  install unattended-upgrades
RUN apt-get -y  install protobuf-compiler
RUN apt-get -y install python3.7 && apt-get -y install python3-pip && pip3 install --upgrade pip
RUN python3.7 -m pip install -r requirements.txt
# Create build directory and navigate inside
RUN cd src/build && make && cd ..

CMD ["python3.7", "server.py"]
