FROM ns:3.29

RUN apt-get update && apt-get install -y python3-dev python3-pip

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app

RUN pip3 install -r requirements.txt
COPY . /app

ENTRYPOINT ["python3"]
CMD ["network_simulator/main.py"]
