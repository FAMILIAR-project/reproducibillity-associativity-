# Use a base image with a Unix-like environment
FROM ubuntu:latest

# Set a working directory
WORKDIR /workspace

# Install necessary packages
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    software-properties-common

# Add the sbt repository GPG key and repository
RUN curl -sL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x2EE0EA64E40A89B84B2DF73499E82A75642AC823" | gpg --dearmor | tee /usr/share/keyrings/sbt-archive-keyring.gpg > /dev/null
RUN echo "deb [signed-by=/usr/share/keyrings/sbt-archive-keyring.gpg] https://repo.scala-sbt.org/scalasbt/debian all main" | tee /etc/apt/sources.list.d/sbt.list

# Install Python, JDK, GCC, Clang, sbt, Node.js, Rust, a Lisp interpreter
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    default-jdk \
    gcc \
    clang \
    sbt \
    nodejs \
    npm \
    rustc \
    cargo \
    clisp \
 && rm -rf /var/lib/apt/lists/*

# Get julia and add it to the PATH
RUN cd /opt && curl -O https://julialang-s3.julialang.org/bin/linux/x64/1.10/julia-1.10.2-linux-x86_64.tar.gz \
    && tar zxvf julia-1.10.2-linux-x86_64.tar.gz 
ENV PATH="${PATH}:/opt/julia-1.10.2"

# Numpy for eval.py
RUN python3 -m pip install numpy

# Perl needs enum package
RUN cpan install Getopt::Long enum


# Optionally, set environment variables, like JAVA_HOME
# ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64

# Copy your eval.py (and any other necessary files) into the container
COPY . /workspace

# Command to run on container start (modify as needed)
CMD ["python3", "eval.py"]
