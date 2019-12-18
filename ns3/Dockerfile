FROM ubuntu:18.04

# openmpi libraries: unsure if needed, MPI support
# autoconf, cvs, bzr and unrar: only for bake needed
# tcpdump: only needed for convenience
# git: only for installing bake

RUN apt-get update \
	&& apt-get install -y gcc g++ python python-dev python3 python3-dev unzip mercurial \
		openmpi-bin openmpi-common openmpi-doc libopenmpi-dev \
		autoconf cvs bzr unrar \
		gsl-bin libgsl-dev libgsl23 libgslcblas0 \
		tcpdump \
		libxml2 libxml2-dev \
		vtun lxc \
		git
		
WORKDIR /ns3

ENV BAKE_HOME=/ns3/bake 
ENV PATH=$PATH:$BAKE_HOME
ENV PYTHONPATH=$PYTHONPATH:$BAKE_HOME

RUN git clone https://gitlab.com/nsnam/bake
RUN bake.py configure -e ns-3.29 \
	&& bake.py deploy \
