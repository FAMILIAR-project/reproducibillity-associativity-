# Use a base image with a Unix-like environment
FROM ubuntu:22.04
ENV DEBIAN_FRONTEND noninteractive

# Set a working directory
WORKDIR /workspace

# Install necessary packages
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    software-properties-common \
    binutils \
    git \
    gnupg2 \
    libc6-dev \
    libcurl4-openssl-dev \
    libedit2 \
    libgcc-9-dev \
    libpython3.8 \
    libsqlite3-0 \
    libstdc++-9-dev \
    libxml2-dev \
    libz3-dev \
    pkg-config \
    tzdata \
    unzip \
    zlib1g-dev

# Add R repository
RUN curl -sL "https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc" | gpg --dearmor | tee /usr/share/keyrings/r-project.gpg > /dev/null
RUN echo "deb [signed-by=/usr/share/keyrings/r-project.gpg] https://cloud.r-project.org/bin/linux/ubuntu $(lsb_release -cs)-cran40/" | tee -a /etc/apt/sources.list.d/r-project.list

# Add the sbt repository GPG key and repository
RUN curl -sL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x2EE0EA64E40A89B84B2DF73499E82A75642AC823" | gpg --dearmor | tee /usr/share/keyrings/sbt-archive-keyring.gpg > /dev/null
RUN echo "deb [signed-by=/usr/share/keyrings/sbt-archive-keyring.gpg] https://repo.scala-sbt.org/scalasbt/debian all main" | tee /etc/apt/sources.list.d/sbt.list

# Install Python, JDK, GCC, Clang, sbt, Node.js, Rust, a Lisp interpreter
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-numpy \
    default-jdk \
    gcc \
    clang \
    i686-w64-mingw32-gcc \
    sbt \
    nodejs \
    npm \
    rustc \
    cargo \
    clisp \
    r-base \
    opam \
    ocaml \
    sbcl \
    bc \
 && rm -rf /var/lib/apt/lists/*

# Get julia and add it to the PATH
RUN cd /opt && curl -LO https://julialang-s3.julialang.org/bin/linux/x64/1.10/julia-1.10.2-linux-x86_64.tar.gz \
    && tar zxvf julia-1.10.2-linux-x86_64.tar.gz 
ENV PATH="${PATH}:/opt/julia-1.10.2/bin"
RUN julia -e 'import Pkg;Pkg.add("ArgParse")'

# Add go
RUN cd /opt && curl -LO https://go.dev/dl/go1.22.2.linux-amd64.tar.gz \
    && tar zxf go1.22.2.linux-amd64.tar.gz 
ENV PATH="${PATH}:/opt/go/bin"

# Swift
RUN cd /opt && curl -LO https://download.swift.org/swift-5.10-release/ubuntu2204/swift-5.10-RELEASE/swift-5.10-RELEASE-ubuntu22.04.tar.gz \
    && tar xzf swift-5.10-RELEASE-ubuntu22.04.tar.gz
ENV PATH="${PATH}:/opt/swift-5.10-RELEASE-ubuntu22.04/usr/bin"

# Perl needs enum package
RUN cpan install Getopt::Long enum

# Optionally, set environment variables, like JAVA_HOME
# ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64

# Copy your eval.py (and any other necessary files) into the container
COPY . /workspace

# Javascript
RUN cd /workspace/js && npm install

# Command to run on container start (modify as needed)
CMD ["python3", "eval.py"]
