#!/bin/bash

# controls_dev sets pip up to look at a local pypi server, which is incomplete
module unload controls_dev

if [ -d "./.venv" ]; then
rm -rf .venv
fi

module load python/3.11 && module load uv

uv sync --editable --group dev    # This creates venv with i19-bluesky in dev editable mode
source .venv/bin/activate

pre-commit install

module unload python/3.11 && module unload uv

# Local version of dodal
if [ ! -d "../dodal" ]; then
  git clone git@github.com:DiamondLightSource/dodal.git ../dodal
fi

uv pip install -e ../dodal/

pre-commit run --all-files
pytest tests/unit_tests
