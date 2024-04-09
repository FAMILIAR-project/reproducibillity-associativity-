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

# Optionally, set environment variables, like JAVA_HOME
# ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64

# Copy your eval.py (and any other necessary files) into the container
COPY . /workspace

# Command to run on container start (modify as needed)
CMD ["python3", "eval.py"]
