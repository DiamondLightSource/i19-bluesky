# Getting started

## Development environment

- Clone this repo: [git@github.com:DiamondLightSource/i19-bluesky.git](git@github.com:DiamondLightSource/i19-bluesky.git)
- To install a dev environment run ./dev_install.sh. Note that this will also clone and install a local version of dodal, as the i19-bluesky package makes use of the devices instantiated there.

The recommended IDE is vscode, and a workspace which includes dodal has been set up in the repo. This can be used on a DLS machine as follows:

```bash
cd /path/to/i19-bluesky
module load vscode
code ./.vscode/i19-bluesky.code-workspace
```

If you use vs code, you may need to set the python interpreter for both repositories to the one from the virtual environment created in `.venv`.


## Supported Python versions

As a standard for the python versions to support, we are using the [numpy deprecation policy](https://numpy.org/neps/nep-0029-deprecation_policy.html).

Currently supported versions are: 3.10, 3.11, 3.12.
