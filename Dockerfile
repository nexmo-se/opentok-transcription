FROM debian:buster

# Create the working directory
RUN mkdir -p /usr/src/app

# Set the working directory
WORKDIR /usr/src/app

# Copy the folder content to the working directory
COPY . /usr/src/app

RUN apt-get update

RUN apt-get -y install gnupg2 && apt-get -y install wget && echo "deb https://dl.bintray.com/tokbox/debian buster main" | tee -a /etc/apt/sources.list && wget -O- -q https://bintray.com/user/downloadSubjectPublicKey?username=bintray | apt-key add - && apt-get update && apt-get -y install libopentok-dev

RUN apt-get -y install libcairo2-dev libjpeg-dev libgif-dev

RUN apt-get -y install python3.7 && apt-get -y install python3-pip

RUN pip3 install -r requirements.txt

# Create build directory and navigate inside
RUN mkdir src/build && cd src/build

RUN CC=clang CXX=clang++ cmake ..
RUN make
RUN cd ..

CMD ["python3.7", "server.py"]
