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

# precreate user vsts 
RUN groupadd --gid 1001 vsts && \
    useradd -s /bin/bash --uid 1001 --gid 1001 -m vsts

USER vsts

# precreate CI environment for user vsts
COPY devops_pipelines/build_agent/ci_dependencies.yml /home/vsts/.

RUN conda env create -f /home/vsts/ci_dependencies.yml -n ci 

# activate environment (Azure Pipelines won't use bash to execute)
ENV PATH /home/vsts/.conda/envs/ci/bin:$PATH

# Issue with PyJWT change in 2.0 from 1.7.  Install msal 1.6 effectively installs PyJWT 1.7
RUN yes | pip uninstall msal && yes | pip install msal==1.6.0

# switch back to root
USER root