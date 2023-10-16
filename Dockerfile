FROM python:3.12-slim-bullseye
RUN apt-get update && apt-get install -y git

WORKDIR /src

COPY requirements.txt /src
RUN pip install --no-cache-dir -r requirements.txt

CMD ["/bin/bash"]