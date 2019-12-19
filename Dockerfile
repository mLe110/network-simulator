FROM ns:3.29

RUN apt-get update && apt-get install -y python3-dev python3-pip

# TODO refactor
COPY ns3/networks/tap-wifi-containers.cc source/ns-3.29/scratch/tap-wifi-containers.cc
COPY ns3/networks/tap-wifi-full_setup.cc source/ns-3.29/scratch/tap-wifi-full_setup.cc

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app

RUN pip3 install -r requirements.txt
COPY . /app

ENTRYPOINT ["python3"]
CMD ["network_simulator/main.py"]
