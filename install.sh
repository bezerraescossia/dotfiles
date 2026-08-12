#!/bin/bash
# Garante compilador C do sistema antes do Homebrew
if ! command -v cc &> /dev/null; then
  sudo apt update
  sudo apt install -y build-essential
fi

brew bundle
