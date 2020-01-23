FROM ns:3.29

RUN apt-get update && apt-get install -y python3-dev python3-pip libboost-all-dev libvirt-bin libvirt-dev

COPY ns3/networks/ source/ns-3.29/scratch/

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app

ENV WAF /ns3/source/ns-3.29/waf
ENV PYTHONPATH=$PYTHONPATH:/app

RUN pip3 install -r requirements.txt
COPY . /app

WORKDIR /ns3/source/ns-3.29

EXPOSE 5000

ENTRYPOINT ["python3"]
CMD ["/app/network_simulator/main.py"]
