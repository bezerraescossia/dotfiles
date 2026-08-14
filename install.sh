#!/usr/bin/env bash
#
# setup.sh
# Bootstraps a dev machine: build tools -> Homebrew -> brew bundle -> dotfiles (stow)
#
set -euo pipefail
# ---------- flags ----------
# --nvim: minimal mode for containers that only need to run Neovim + its
# tooling (e.g. cloning this repo inside a container to develop with nvim).
# Skips the full Brewfile and the zsh/powerlevel10k shell takeover, installing
# only the brew formulas home/.config/nvim and its Mason-managed tools
# (LSPs/formatters/debuggers) actually need, then stows dotfiles as usual.
NVIM_ONLY=0
for arg in "$@"; do
  case "$arg" in
    --nvim) NVIM_ONLY=1 ;;
    *) ;;
  esac
done
NVIM_BREW_PACKAGES=(git stow neovim ripgrep fd tree-sitter node unzip lazygit xclip gcc rust)
# ---------- logging helpers ----------
LOG_FILE="${LOG_FILE:-/tmp/.setup-$(date +%Y%m%d-%H%M%S).log}"
log()  { printf '[%s] %s\n' "$(date '+%H:%M:%S')" "$*" | tee -a "$LOG_FILE"; }
die()  { log "❌ ERROR: $*"; exit 1; }
trap 'die "Script failed at line $LINENO (last command: $BASH_COMMAND)"' ERR
log "Log file: $LOG_FILE"
# ---------- 1. System C compiler (Linux only) ----------
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
BREW_BIN=""
if [[ -x "/opt/homebrew/bin/brew" ]]; then
  BREW_BIN="/opt/homebrew/bin/brew"
elif [[ -x "/usr/local/bin/brew" ]]; then
  BREW_BIN="/usr/local/bin/brew"
elif [[ -x "/home/linuxbrew/.linuxbrew/bin/brew" ]]; then
  BREW_BIN="/home/linuxbrew/.linuxbrew/bin/brew"
fi

if command -v brew >/dev/null 2>&1; then
  log "Homebrew is already installed: $(brew --version | head -n 1)"
elif [[ -n "$BREW_BIN" ]]; then
  log "Homebrew binary found at $BREW_BIN but not on PATH yet."
else
  log "Homebrew not found. Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  if [[ -x "/opt/homebrew/bin/brew" ]]; then
    BREW_BIN="/opt/homebrew/bin/brew"
  elif [[ -x "/usr/local/bin/brew" ]]; then
    BREW_BIN="/usr/local/bin/brew"
  elif [[ -x "/home/linuxbrew/.linuxbrew/bin/brew" ]]; then
    BREW_BIN="/home/linuxbrew/.linuxbrew/bin/brew"
  fi
  [[ -n "$BREW_BIN" ]] || die "Homebrew install ran but no brew binary was found in the usual locations."
  log "Homebrew installed successfully."
fi

# NOTE: this runs regardless of which branch above we took (already-installed,
# found-but-not-on-PATH, or freshly-installed). The old version of this script only
# did `eval "$(brew shellenv)")` inside the "just installed" branch, so on a machine
# that already had Homebrew installed, the running script's PATH never picked up
# brew's bin dir — which meant e.g. `which zsh` later in the script (zsh comes from
# the Brewfile via brew bundle) could silently fail to find the brew-installed zsh.
if [[ -n "$BREW_BIN" ]]; then
  eval "$("$BREW_BIN" shellenv)"
fi
command -v brew >/dev/null 2>&1 || die "brew is still not on PATH after setup."

# Persist it for FUTURE sessions too (the original script only fixed the current shell).
# NOTE: we write to BOTH .bashrc and .zshrc, not just "$HOME/.$(basename "$SHELL")rc",
# because later in this script we chsh the user to zsh regardless of what $SHELL is
# right now. If we only wrote to the current $SHELL's rc file, a bash user would get
# brew shellenv in ~/.bashrc, then get switched to zsh, and zsh would never source it —
# leaving brew-installed tools (nvim, lazygit, stow, ...) missing from PATH.
for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
  if ! grep -qs "brew shellenv" "$rc" 2>/dev/null; then
    echo "eval \"\$($BREW_BIN shellenv)\"" >> "$rc"
    log "Added brew shellenv to $rc"
  fi
done
# ---------- 3. brew bundle ----------
if [[ "$NVIM_ONLY" -eq 1 ]]; then
  log "--nvim mode: installing only the brew formulas nvim needs: ${NVIM_BREW_PACKAGES[*]}"
  brew install "${NVIM_BREW_PACKAGES[@]}"
  log "Nvim brew formulas installed successfully."
else
  log "Installing all dependencies via brew bundle..."
  if [[ -f "Brewfile" ]]; then
    brew bundle
    log "Brew bundle installed successfully."
  else
    log "⚠️  No Brewfile found in $(pwd); skipping 'brew bundle'."
  fi
  # Add zsh as default shell
  echo "$(which zsh)" | sudo tee -a /etc/shells
  chsh -s $(which zsh)
  if [[ -d "$HOME/powerlevel10k" ]]; then
    log "powerlevel10k already cloned at ~/powerlevel10k; skipping clone."
  else
    git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ~/powerlevel10k
  fi
  if ! grep -qs 'source ~/powerlevel10k/powerlevel10k.zsh-theme' ~/.zshrc 2>/dev/null; then
    echo 'source ~/powerlevel10k/powerlevel10k.zsh-theme' >>~/.zshrc
    log "Added powerlevel10k source line to ~/.zshrc"
  fi
fi
# ---------- 4. Dotfiles via GNU stow ----------
log "Generating all config files..."
if ! command -v stow >/dev/null 2>&1; then
  log "GNU stow not found; installing via brew..."
  brew install stow
fi
if [[ -d "home" ]]; then
  stow -t "$HOME" home
  log "Config files successfully created."
else
  log "⚠️  'home' directory not found in $(pwd); skipping stow."
fi

if [[ "$NVIM_ONLY" -eq 0 ]]; then
  # zsh does NOT read ~/.bash_profile automatically (that's a bash/sh login-shell convention),
  # so any aliases stowed into ~/.bash_profile would silently never load in an interactive
  # zsh session unless we explicitly source it from ~/.zshrc.
  if [[ -f "$HOME/.bash_profile" ]]; then
    if ! grep -qs '\.bash_profile' "$HOME/.zshrc" 2>/dev/null; then
      echo '[ -f ~/.bash_profile ] && source ~/.bash_profile' >> ~/.zshrc
      log "Added ~/.bash_profile sourcing to ~/.zshrc so its aliases are available in zsh."
    fi
  fi
fi

log "✅ Setup complete."
