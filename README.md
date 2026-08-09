# My Dotfiles

This repository contains personal system configurations, managed cleanly using **[GNU Stow](https://www.gnu.org/software/stow/)**.

GNU Stow creates symlinks from subdirectories in this repository directly into your `$HOME` directory without duplicating or manually moving files.

---

## 📁 Repository Structure

```
~/dotfiles/
├── nvim/               # Package for Neovim configuration
│   └── .config/
│       └── nvim/       # Symlinked to ~/.config/nvim
├── tmux/               # Package for Tmux configuration
│   └── .tmux.conf      # Symlinked to ~/.tmux.conf
├── wezterm/            # Package for Wezterm configuration
│   └── .wezterm.lua    # Symlinked to ~/.wezterm.lua or Windows user profile
└── README.md
```

---

## 🚀 Setting Up on a New Machine

The recommended setup command is:

```bash
git clone <YOUR-GIT-REPO-URL> ~/dotfiles
cd ~/dotfiles
make install
```

`make install` checks for the command-line tools used by AstroNvim and tmux,
links the `nvim`, `tmux`, and `wezterm` packages into your home directory, and
installs the tmux Plugin Manager (TPM). WezTerm itself and the font are installed
separately using the package manager for your operating system. Run
`make install-tmux-plugins` after TPM is installed if you want to fetch the
configured tmux plugins immediately.

Follow these steps to restore your configuration on a fresh machine or secondary PC:

### 1. Install Prerequisites
Ensure these prerequisites are installed:

- Git, GNU Stow, Neovim, and tmux
- A C compiler, `tree-sitter` CLI, ripgrep (`rg`), fd, and lazygit
- Go disk-usage (`gdu`) and bottom (`btm`)
- Python 3, `uv`, and Node.js
- A clipboard command (`xclip`, `xsel`, `wl-copy`, `pbcopy`, or `clip.exe`)
- Hack Nerd Font (the configured WezTerm font)

- **Debian / Ubuntu**:
  ```bash
  sudo apt update && sudo apt install -y git stow
  ```
- **Arch Linux**:
  ```bash
  sudo pacman -S git stow
  ```
- **macOS** (Homebrew):
  ```bash
  brew install git stow
  ```

### 2. Clone the Repository
Clone this repository into your `$HOME` directory:

```bash
git clone <YOUR-GIT-REPO-URL> ~/dotfiles
cd ~/dotfiles
```

### 3. Link Configurations with Stow
Run `stow` for all packages or specific packages you want to install:

```bash
# Stow Linux / WSL packages
stow nvim
stow tmux
stow wezterm  # Symlinks to ~/.wezterm.lua in WSL
```

> **Note:** If target files already exist in your home directory (e.g. an existing default `~/.tmux.conf`), `stow` will report a conflict and refuse to overwrite them. Remove or back up those existing files before running `stow`.

---

## 🪟 Windows / WSL Setup for WezTerm

If you run **WezTerm natively on Windows** and spawn WSL sessions inside it, WezTerm looks for `.wezterm.lua` in your Windows User Profile (`C:\Users\<username>\.wezterm.lua` / `/mnt/c/Users/<username>/.wezterm.lua`).

To link your WezTerm config from this repo directly into Windows:

### Method A: Symlink via WSL Terminal (Recommended)
Run this command inside your WSL shell:

```bash
ln -sf ~/dotfiles/wezterm/.wezterm.lua /mnt/c/Users/$(whoami)/.wezterm.lua
```

### Method B: Native Windows Symlink (CMD / PowerShell)
If Windows native symlinking is required, open CMD in Windows:

```cmd
cmd.exe /c "mklink C:\Users\%USERNAME%\.wezterm.lua \\wsl.localhost\Ubuntu\home\%USERNAME%\dotfiles\wezterm\.wezterm.lua"
```

---

## ➕ How to Add New Dotfiles to This Repository

When you want to add a new configuration (e.g., `~/.zshrc`, `~/.gitconfig`, or `~/.config/alacritty`) to this repository, follow the GNU Stow mirroring pattern:

### Standard Rule
Inside your `~/dotfiles` folder, create a package directory (e.g., `package-name/`) and replicate the relative path from `$HOME`.

---

### Example 1: Adding a file directly in `$HOME` (e.g. `~/.zshrc`)

1. **Create the package folder**:
   ```bash
   mkdir -p ~/dotfiles/zsh
   ```

2. **Move your config into the package folder**:
   ```bash
   mv ~/.zshrc ~/dotfiles/zsh/.zshrc
   ```

3. **Symlink it with Stow**:
   ```bash
   cd ~/dotfiles
   stow zsh
   ```

---

### Example 2: Adding a folder in `~/.config/` (e.g. `~/.config/alacritty`)

1. **Create the package directory mirroring the `.config` subpath**:
   ```bash
   mkdir -p ~/dotfiles/alacritty/.config
   ```

2. **Move your configuration folder into place**:
   ```bash
   mv ~/.config/alacritty ~/dotfiles/alacritty/.config/
   ```

3. **Symlink it with Stow**:
   ```bash
   cd ~/dotfiles
   stow alacritty
   ```

---

## ⚙️ GNU Stow Cheat Sheet

| Command | Action |
| :--- | :--- |
| `stow <package>` | Create symlinks for `<package>` in `$HOME` |
| `stow -D <package>` | **Unstow**: Remove symlinks for `<package>` |
| `stow -R <package>` | **Restow**: Re-link `<package>` (useful when files are added/removed) |
| `stow --adopt <package>` | Adopt existing home files into the repo package and create symlinks |
| `stow -n -v <package>` | **Dry run**: Preview symlink actions without modifying files |

---

## 🛠️ Environment Prerequisites & Tools

- [GNU Stow](https://www.gnu.org/software/stow/)
- [Neovim](https://neovim.io/)
- [Tmux](https://github.com/tmux/tmux)
- [WezTerm](https://wezfurlong.org/wezterm/)
