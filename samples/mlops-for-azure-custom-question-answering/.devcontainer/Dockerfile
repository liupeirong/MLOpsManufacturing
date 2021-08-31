# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.163.1/containers/typescript-node/.devcontainer/base.Dockerfile

# [Choice] Node.js version: 14, 12, 10
ARG VARIANT="14-buster"
FROM mcr.microsoft.com/vscode/devcontainers/typescript-node:0-${VARIANT}

# Fix GPG error: https://github.com/yarnpkg/yarn/issues/4453
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -

# Install Azure CLI with Bicep and Azure DevOps Extension
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash \
    && az bicep install \
    && az extension add --name azure-devops

# [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>

# [Optional] Uncomment if you want to install an additional version of node using nvm
# ARG EXTRA_NODE_VERSION=10
# RUN su node -c "source /usr/local/share/nvm/nvm.sh && nvm install ${EXTRA_NODE_VERSION}"

# [Optional] Uncomment if you want to install more global node packages
# RUN su node -c "npm install -g <your-package-list -here>"

# Install Conda
USER node

WORKDIR /home/node

RUN curl -fsSLo Miniconda3-latest-Linux-x86_64.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh \
    && echo PATH="/home/node/miniconda3/bin":$PATH >> .bashrc \
    && exec bash \
    && conda --version

ENV PATH /home/node/miniconda3/bin:$PATH

RUN conda init bash \
    && echo 'conda activate devenv' >> .bashrc

# Sometimes updates are needed which open up a prompt
RUN az config set extension.use_dynamic_install=yes_without_prompt

USER root