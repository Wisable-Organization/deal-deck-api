#!/bin/bash
# One-line command to install Poetry, add to PATH, and install dependencies
pip install --user poetry==2.2.1 && export PATH="$HOME/.local/bin:$PATH" && poetry install --no-dev

