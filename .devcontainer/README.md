# DevContainer

The current devcontainer was build and tested on Windows 10 with Docker for Windows with WSL2 support enabled.
In general in this setting it is recommended to place the repo under WSL2 file system.

The current devcontainer **won't build and/or run correctly** if the repo is cloned under the Windows filesystem.

## Prerequisites

* Docker CE or Docker for Windows
* In case Docker for Windows repo needs to be cloned within WSL2 file system
* Git
* Visual Studio Code
* Visual Studio Code Extension `ms-vscode-remote.remote-containers`
* [Personal SSH key](https://docs.microsoft.com/en-us/azure/devops/repos/git/use-ssh-keys-to-authenticate?view=azure-devops)

## Setup

* Clone the repo (within WSL2 file system)
* Open the folder in vscode
* Reopen in Container [SHIFT+CTRL+P] `>Remote-Containers: Rebuild and Reopen in Container`

## Features

* Using non-root user
* local machine Linux/WSL user's `~/.ssh` folder is mounted so `Personal SSH keys` can be used
* Docker CLI in container will use local machine's docker service
(images pulled or created are persisted on local machine's storage)
* Conda environment with `ml_model/dev_dependencies.yml` is pre-activated
* Azure CLI
