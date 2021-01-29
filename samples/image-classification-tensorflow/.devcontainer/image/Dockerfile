# We need Ubuntu as a base image see https://docs.microsoft.com/en-us/azure/machine-learning/how-to-deploy-custom-docker-image#build-a-custom-base-image
FROM ubuntu:18.04

# Path to current sample
ARG SAMPLE_PATH=samples/image-classification-tensorflow

ENV DEBIAN_FRONTEND=noninteractive

RUN echo "APT::Get::Assume-Yes \"true\";" > /etc/apt/apt.conf.d/90assumeyes

RUN apt-get update \
    && apt-get -y install --no-install-recommends apt-utils dialog sudo 2>&1 \
    && apt-get -y install \
    git \
    jq \
    openssh-client \
    less \
    iproute2 \
    procps \
    lsb-release \
    apt-transport-https \
    software-properties-common \
    ca-certificates \
    curl \
    build-essential \
    gnupg2 \
    bash-completion \
    unzip \
    iputils-ping \
    libcurl4 \
    libunwind8 \
    netcat

# Map local machines Docker GID (retrieved by dockergid.sh) to enable non-root user to use docker on local machine
COPY $SAMPLE_PATH/.devcontainer/dockergid /tmp
RUN DOCKER_GID=`cat /tmp/dockergid` \
    && groupadd --gid $DOCKER_GID docker
RUN rm /tmp/dockergid
# Install Docker CLI
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - \
    && add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian buster stable" \
    && apt-get update \
    && apt install docker-ce

# Install Azure CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash \
    && az extension add --name azure-devops \
    && az extension add --name azure-cli-ml

# Cleanup
RUN apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*    

# set up git-prompt.sh
WORKDIR /usr/local/bin
COPY $SAMPLE_PATH/.devcontainer/image/git-prompt.sh .
RUN echo "source /usr/local/bin/git-prompt.sh" >> ~/.bashrc
RUN echo "PROMPT_COMMAND='__posh_git_ps1 \"\u@\h:\w \" \"\\\$ \";'$PROMPT_COMMAND" >> ~/.bashrc

# enable git completion
RUN echo "source /usr/share/bash-completion/completions/git"  >> ~/.bashrc

# Add miniconda
RUN cd ~ && curl -Os https://repo.anaconda.com/miniconda/Miniconda3-4.5.11-Linux-x86_64.sh && \
    /bin/bash ~/Miniconda3-4.5.11-Linux-x86_64.sh -b -p /opt/conda && \
    rm ~/Miniconda3-4.5.11-Linux-x86_64.sh && \
    /opt/conda/bin/conda clean -tipsy && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc
ENV PATH /opt/conda/bin/:$PATH
RUN conda update conda

# Add ssh-agent/ssh-add to .bashrc
COPY $SAMPLE_PATH/.devcontainer/image/ssh-agent.sh /tmp
RUN cat /tmp/ssh-agent.sh >> ~/.bashrc \
    && rm /tmp/ssh-agent.sh

ENV DEBIAN_FRONTEND=noninteractive

RUN echo "APT::Get::Assume-Yes \"true\";" > /etc/apt/apt.conf.d/90assumeyes

RUN apt-get update && apt-get install -y sudo

# --------------------------------------------------------------------------
# vscode
# --------------------------------------------------------------------------
RUN groupadd --gid 1000 vscode \
    && useradd -s /bin/bash --uid 1000 --gid 1000 -m vscode \
    && usermod -a -G docker vscode \
    && apt-get install -y sudo \
    && echo vscode ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/vscode\
    && chmod 0440 /etc/sudoers.d/vscode 

# Copy enhanced /root/.bashrc to vscode user
RUN cp ~/.bashrc /home/vscode/.
RUN chown 1000:1000 /home/vscode/.bashrc
RUN chown -R 1000:root /opt/conda

RUN echo 'vscode:vscode!20' | chpasswd 

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

# Switch back to dialog for any ad-hoc use of apt-get
ENV DEBIAN_FRONTEND=dialog

# Copy conda dependencies
WORKDIR /tmp
COPY $SAMPLE_PATH/local_development/dev_dependencies.yml .

# Create conda environment for vscode user
USER vscode
RUN conda env update -f dev_dependencies.yml -n base