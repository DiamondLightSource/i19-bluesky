# The devcontainer should use the developer target and run as root with podman
# or docker with user namespaces.
ARG PYTHON_VERSION=3.11@sha256:a3f963d22cc2bd1b0e9a62c8e6f31b3bd3340d554fae00cc312c3359b61a6d7e
FROM python:${PYTHON_VERSION} AS developer

# Add any system dependencies for the developer/build environment here
RUN apt-get update && apt-get install -y --no-install-recommends \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# Set up a virtual environment and put it in PATH
RUN python -m venv /venv
ENV PATH=/venv/bin:$PATH
