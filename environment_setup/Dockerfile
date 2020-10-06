FROM conda/miniconda3

COPY ml_model/ci_dependencies.yml /setup/

# activate environment
ENV PATH /usr/local/envs/mlopstensorflow_ci/bin:$PATH

RUN conda update -n base -c defaults conda && \
    conda install python=3.7.5 && \
    conda env create -f /setup/ci_dependencies.yml && \
    /bin/bash -c "source activate mlopstensorflow_ci" && \
    az extension add -n azure-cli-ml && \
    az --version && \
    chmod -R 777 /usr/local/envs/mlopstensorflow_ci/lib/python3.7
