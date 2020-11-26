FROM conda/miniconda3

ENV PATH /opt/conda/bin/:$PATH
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV LANGUAGE C.UTF-8

RUN conda update -n base -c defaults conda && \
    conda install python=3.7.5 && \
    apt-get update && \
    apt-get install gcc python3-dev -y

# Install Azure CLI
RUN apt-get update && \
    apt-get install ca-certificates curl apt-transport-https lsb-release gnupg -y && \
    curl -sL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | tee /etc/apt/trusted.gpg.d/microsoft.gpg > /dev/null && \
    AZ_REPO=$(lsb_release -cs) && \
    echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ $AZ_REPO main" | tee /etc/apt/sources.list.d/azure-cli.list && \
    apt-get update && \
    apt-get install azure-cli -y && \
    az --version

# az cli extension defaults to $HOME/.azure/cliextensions
# which doesn't exist when running in ADO because ADO runs as 
# a new user vsts_azpcontainer
RUN mkdir /opt/azcliextensions 
ENV AZURE_EXTENSION_DIR /opt/azcliextensions
RUN az extension add -n azure-cli-ml

# add and activate user buildagent 
RUN groupadd --gid 1000 buildagent && \
    useradd -s /bin/bash --uid 1000 --gid 1000 -m buildagent

USER buildagent

# activate CI environment
COPY ml_model/ci_dependencies.yml /home/buildagent/.

RUN conda env create -f /home/buildagent/ci_dependencies.yml -n ci && \
    echo "source activate ci" >> ~/.bashrc