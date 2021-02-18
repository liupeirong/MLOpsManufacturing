FROM ubuntu:18.04

ARG MINI_CONDA_VERSION=py38_4.8.3
ARG CONDA_VERSION=4.8.3
ARG PYTHON_VERSION=3.8
ARG AZUREML_SDK_VERSION=1.16.0
ARG INFERENCE_SCHEMA_VERSION=1.1.0

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH /opt/miniconda/bin:$PATH
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update --fix-missing && \
    apt-get install -y wget bzip2 && \
    apt-get install -y fuse && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*

# Install Kaldi dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        g++ \
        make \
        automake \
        autoconf \
        bzip2 \
        unzip \
        wget \
        sox \
        libtool \
        git \
        subversion \
        python2.7 \
        python3 \
        zlib1g-dev \
        ca-certificates \
        gfortran \
        patch \
        ffmpeg \
        gawk \
	vim && \
    rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python2.7 /usr/bin/python

# Install Kaldi
RUN git clone --depth 1 https://github.com/kaldi-asr/kaldi.git /opt/kaldi && \
    cd /opt/kaldi/tools && \
    ./extras/install_mkl.sh && \
    make -j $(nproc) && \
    cd /opt/kaldi/src && \
    ./configure --shared && \
    make depend -j $(nproc) && \
    make -j $(nproc) && \
    find /opt/kaldi -type f \( -name "*.o" -o -name "*.la" -o -name "*.a" \) -exec rm {} \; && \
    find /opt/intel -type f -name "*.a" -exec rm {} \; && \
    find /opt/intel -type f -regex '.*\(_mc.?\|_mic\|_thread\|_ilp64\)\.so' -exec rm {} \; && \
    rm -rf /opt/kaldi/.git

# Install SRILM
COPY srilm.tar.gz /opt/kaldi/tools
RUN cd /opt/kaldi/tools && \
    ./install_srilm.sh

# Continuer Azure ML conda setup
RUN useradd --create-home dockeruser
WORKDIR /home/dockeruser
USER dockeruser

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-${MINI_CONDA_VERSION}-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p ~/miniconda && \
    rm ~/miniconda.sh && \
    ~/miniconda/bin/conda clean -tipsy
ENV PATH="/home/dockeruser/miniconda/bin/:${PATH}"

RUN conda install -y conda=${CONDA_VERSION} python=${PYTHON_VERSION} && \
    pip install azureml-defaults==${AZUREML_SDK_VERSION} inference-schema==${INFERENCE_SCHEMA_VERSION} &&\
    conda clean -aqy && \
    rm -rf ~/miniconda/pkgs && \
    find ~/miniconda/ -type d -name __pycache__ -prune -exec rm -rf {} \;