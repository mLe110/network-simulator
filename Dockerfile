FROM ns:3.29

RUN apt-get update && apt-get install -y python3-dev python3-pip

# TODO refactor
COPY ns3/networks/tap-wifi-containers.cc source/ns-3.29/scratch/tap-wifi-containers.cc
COPY ns3/networks/tap-wifi-full_setup.cc source/ns-3.29/scratch/tap-wifi-full_setup.cc

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app

ENV WAF /ns3/source/ns-3.29/waf
ENV PYTHONPATH=$PYTHONPATH:/app

RUN pip3 install -r requirements.txt
COPY . /app

WORKDIR /ns3/source/ns-3.29
# TODO run container with NET_ADMIN capabilities

#ENTRYPOINT ["python3"]
#CMD ["/app/network_simulator/main.py"]
