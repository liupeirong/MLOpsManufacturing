FROM conda/miniconda3

COPY ml_model/ci_dependencies.yml /setup/

# activate environment
ENV PATH /usr/local/envs/mlopstensorflow_ci/bin:$PATH

RUN conda update -n base -c defaults conda && \
    conda install python=3.7.5 && \
    apt-get update && \
    apt-get install gcc python3-dev -y && \
    conda env create -f /setup/ci_dependencies.yml && \
    /bin/bash -c "source activate mlopstensorflow_ci" && \
    az --version && \
    chmod -R 777 /usr/local/envs/mlopstensorflow_ci/lib/python3.7

# az cli extension defaults to $HOME/.azure/cliextensions
# which doesn't exist when running in ADO because ADO runs as 
# a new user vsts_azpcontainer
RUN mkdir /opt/azcliextensions 
ENV AZURE_EXTENSION_DIR /opt/azcliextensions
RUN az extension add -n azure-cli-ml
