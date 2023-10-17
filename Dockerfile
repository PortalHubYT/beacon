# Use the Python 3.12-slim-bullseye as the base image
FROM python:3.12-slim-bullseye

# Install git using apt-get
RUN apt-get update && apt-get install -y git

# Set the working directory inside the container to /src
WORKDIR /src

# Install the Python packages needed for this stream
RUN pip install --no-cache-dir TikTokLive
RUN pip install --no-cache-dir shulker
RUN pip install --no-cache-dir dill
RUN pip install --no-cache-dir redis
RUN pip install --no-cache-dir prompt_toolkit
RUN pip install --no-cache-dir termcolor

# Set the default command to run when starting the container
CMD ["/bin/bash"]
