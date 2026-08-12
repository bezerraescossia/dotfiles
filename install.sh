#!/usr/bin/env bash
#
# setup.sh
# Bootstraps a dev machine: build tools -> Homebrew -> brew bundle -> dotfiles (stow)
#

set -euo pipefail

# ---------- logging helpers ----------
LOG_FILE="${LOG_FILE:-/tmp/.setup-$(date +%Y%m%d-%H%M%S).log}"
log()  { printf '[%s] %s\n' "$(date '+%H:%M:%S')" "$*" | tee -a "$LOG_FILE"; }
die()  { log "❌ ERROR: $*"; exit 1; }

trap 'die "Script failed at line $LINENO (last command: $BASH_COMMAND)"' ERR

log "Log file: $LOG_FILE"

# ---------- 1. System C compiler (Linux only) ----------
# build-essential is a Debian/Ubuntu-apt concept; this block must not run on macOS
# or on distros without apt, or it will fail loudly for no reason.
OS="$(uname -s)"

if [[ "$OS" == "Linux" ]]; then
  if command -v apt >/dev/null 2>&1; then
    if ! command -v cc >/dev/null 2>&1; then
      log "Installing linux build essentials..."
      sudo apt update
      sudo apt install -y build-essential
      log "Linux build essentials installed successfully."
    else
      log "C compiler already present ($(cc --version | head -n 1)). Skipping build-essential."
    fi
  else
    log "⚠️  Non-apt Linux distro detected; skipping build-essential install. Make sure a C compiler is available."
  fi
elif [[ "$OS" == "Darwin" ]]; then
  log "macOS detected; Xcode Command Line Tools provide the C compiler (skipping apt step)."
  if ! command -v cc >/dev/null 2>&1; then
    log "No C compiler found. Installing Xcode Command Line Tools..."
    xcode-select --install || log "⚠️  CLT install prompt may already be open or tools already present."
  fi
else
  log "⚠️  Unrecognized OS '$OS'; skipping compiler bootstrap step."
fi

# ---------- 2. Homebrew ----------
if command -v brew >/dev/null 2>&1; then
  log "Homebrew is already installed: $(brew --version | head -n 1)"
else
  log "Homebrew not found. Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

  # Determine the brew prefix for this platform
  BREW_BIN=""
  if [[ -x "/opt/homebrew/bin/brew" ]]; then
    BREW_BIN="/opt/homebrew/bin/brew"
  elif [[ -x "/usr/local/bin/brew" ]]; then
    BREW_BIN="/usr/local/bin/brew"
  elif [[ -x "/home/linuxbrew/.linuxbrew/bin/brew" ]]; then
    BREW_BIN="/home/linuxbrew/.linuxbrew/bin/brew"
  fi

  [[ -n "$BREW_BIN" ]] || die "Homebrew install ran but no brew binary was found in the usual locations."

  # Load brew into THIS session
  eval "$("$BREW_BIN" shellenv)"

  # Persist it for FUTURE sessions too (the original script only fixed the current shell)
  SHELL_RC="$HOME/.$(basename "$SHELL")rc"
  if ! grep -qs "brew shellenv" "$SHELL_RC" 2>/dev/null; then
    echo "eval \"\$($BREW_BIN shellenv)\"" >> "$SHELL_RC"
    log "Added brew shellenv to $SHELL_RC"
  fi

  command -v brew >/dev/null 2>&1 || die "Homebrew installation failed — brew still not on PATH."
  log "Homebrew installed successfully: $(brew --version | head -n 1)"
fi

# ---------- 3. brew bundle ----------
log "Installing all dependencies via brew bundle..."
if [[ -f "Brewfile" ]]; then
  brew bundle
  log "Brew bundle installed successfully."
else
  log "⚠️  No Brewfile found in $(pwd); skipping 'brew bundle'."
fi

# ---------- 4. Dotfiles via GNU stow ----------
log "Generating all config files..."
if ! command -v stow >/dev/null 2>&1; then
  log "GNU stow not found; installing via brew..."
  brew install stow
fi

if [[ -d "home" ]]; then
  stow home
  log "Config files successfully created."
else
  log "⚠️  'home' directory not found in $(pwd); skipping stow."
fi

log "✅ Setup complete."
