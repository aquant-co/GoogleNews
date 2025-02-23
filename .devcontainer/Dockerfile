FROM mcr.microsoft.com/devcontainers/python:1-3.13-bullseye

ARG PDM_VERSION=2.22.3
ARG PIP_VERSION=25.0.1

ENV PYTHONUNBUFFERED 1


# [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>


# [Optional] If your requirements rarely change, uncomment this section to add them to the image.
# COPY requirements.txt /tmp/pip-tmp/
# RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
#    && rm -rf /tmp/pip-tmp
RUN pip install --no-cache-dir --upgrade pip==${PIP_VERSION} pdm==${PDM_VERSION}


USER vscode
RUN pdm completion bash > ~/.bash_completion
