FROM debian:buster

RUN apt-get update

RUN apt-get -y install libsdl2-dev make wget

RUN apt-get -y install gnupg2 && echo "deb https://dl.bintray.com/tokbox/debian buster main" | tee -a /etc/apt/sources.list && wget -O- -q https://bintray.com/user/downloadSubjectPublicKey?username=bintray | apt-key add - && apt-get update && apt-get -y install libopentok-dev

RUN echo "deb http://apt.llvm.org/buster/ llvm-toolchain-buster main" >> /etc/apt/sources.list
RUN echo "deb-src http://apt.llvm.org/buster/ llvm-toolchain-buster main" >> /etc/apt/sources.list
RUN echo "deb http://apt.llvm.org/buster/ llvm-toolchain-buster-10 main" >> /etc/apt/sources.list
RUN echo "deb-src http://apt.llvm.org/buster/ llvm-toolchain-buster-10 main" >> /etc/apt/sources.list
RUN echo "deb http://apt.llvm.org/buster/ llvm-toolchain-buster-11 main" >> /etc/apt/sources.list
RUN echo "deb-src http://apt.llvm.org/buster/ llvm-toolchain-buster-11 main" >> /etc/apt/sources.list

RUN wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key| apt-key add -

RUN apt-get update
RUN apt-get -y install clang-11

RUN export CMAKE_C_COMPILER=clang-11
RUN export CMAKE_CXX_COMPILER=clang++-11

RUN apt-get -y install wget && wget https://github.com/Kitware/CMake/releases/download/v3.15.2/cmake-3.15.2.tar.gz && tar -zxvf cmake-3.15.2.tar.gz && cd cmake-3.15.2 && CC=clang++-11 ./bootstrap && make && make install && cmake --version

# Create the working directory
RUN mkdir -p /usr/src/app

# Set the working directory
WORKDIR /usr/src/app

# Copy the folder content to the working directory
COPY . /usr/src/app



RUN apt-get -y install libcairo2-dev libjpeg-dev libgif-dev

RUN apt-get -y install python3.7 && apt-get -y install python3-pip && pip3 install --upgrade pip

RUN apt-get -y install cloud-init && apt-get install -y python3-distro-info && apt-get -y install iotop && apt-get -y install curl && apt-get -y install libcurl4-openssl-dev libssl-dev && apt-get -y install python-apt && apt-get -y install python3-distutils-extra && apt-get -y install reportbug && apt -y install unattended-upgrades

RUN python3.7 -m pip install -r requirements.txt

# Create build directory and navigate inside
RUN mkdir src/build && cd src/build

RUN CC=clang CXX=clang++ cmake ..
RUN make
RUN cd ..

CMD ["python3.7", "server.py"]
