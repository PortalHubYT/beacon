# Use the Python 3.12-slim-bullseye as the base image
FROM python:3.12-slim-bullseye

# Install git using apt-get
RUN apt-get update && apt-get install -y git

# Set the working directory inside the container to /src
WORKDIR /src

COPY stream-requirements.txt /src
RUN pip install --no-cache-dir -r stream-requirements.txt

# Set the default command to run when starting the container
CMD ["/bin/bash"]
