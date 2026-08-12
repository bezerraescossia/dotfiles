# My Dotfiles

This repository contains personal system configurations, managed cleanly using **[GNU Stow](https://www.gnu.org/software/stow/)**.

GNU Stow creates symlinks from subdirectories in this repository directly into your `$HOME` directory without duplicating or manually moving files.

---

## 📁 Repository Structure

```
~/dotfiles/
├── home/               # One Stow package mirroring $HOME
│   ├── .config/
│   │   ├── nvim/       # Symlinked to ~/.config/nvim
│   │   └── lazygit/    # Symlinked to ~/.config/lazygit
│   ├── .tmux.conf      # Symlinked to ~/.tmux.conf
│   └── .wezterm.lua    # Symlinked to ~/.wezterm.lua
└── README.md
```

---

## 🚀 Setting Up on a New Machine

The recommended setup command is:

```bash
git clone <YOUR-GIT-REPO-URL> ~/dotfiles
cd ~/dotfiles
brew bundle
stow home
```

`brew bundle` installs the applications and command-line tools listed in
[`Brewfile`](Brewfile). `stow home` then links every configuration into your
home directory. On macOS it also installs WezTerm and Hack Nerd Font; on Linux,
install a graphical WezTerm package separately if it is not available through
your Homebrew setup.

Follow these steps to restore your configuration on a fresh machine or secondary PC:

### 1. Install Prerequisites
Ensure [Homebrew](https://brew.sh/) and the `brew bundle` command are
installed. The `Brewfile` contains the full application and binary list, so no
separate apt/pacman package list is needed.

### 2. Clone the Repository
Clone this repository into your `$HOME` directory:

```bash
git clone <YOUR-GIT-REPO-URL> ~/dotfiles
cd ~/dotfiles
```

### 3. Install Applications and Link Configurations
From the repository root:

```bash
brew bundle
stow home
```

> **Note:** If target files already exist in your home directory (e.g. an existing default `~/.tmux.conf`), `stow` will report a conflict and refuse to overwrite them. Remove or back up those existing files before running `stow`.

---

## 🪟 Windows / WSL Setup for WezTerm

If you run **WezTerm natively on Windows** and spawn WSL sessions inside it, WezTerm looks for `.wezterm.lua` in your Windows User Profile (`C:\Users\<username>\.wezterm.lua` / `/mnt/c/Users/<username>/.wezterm.lua`).

To link your WezTerm config from this repo directly into Windows:

### Method A: Symlink via WSL Terminal (Recommended)
Run this command inside your WSL shell:

```bash
ln -sf ~/dotfiles/home/.wezterm.lua /mnt/c/Users/$(whoami)/.wezterm.lua
```

### Method B: Native Windows Symlink (CMD / PowerShell)
If Windows native symlinking is required, open CMD in Windows:

```cmd
cmd.exe /c "mklink C:\Users\%USERNAME%\.wezterm.lua \\wsl.localhost\Ubuntu\home\%USERNAME%\dotfiles\home\.wezterm.lua"
```

---

## ➕ How to Add New Dotfiles to This Repository

When you want to add a new configuration (e.g., `~/.zshrc`, `~/.gitconfig`, or `~/.config/alacritty`) to this repository, follow the GNU Stow mirroring pattern:

### Standard Rule
Inside `~/dotfiles/home`, mirror the relative path from `$HOME`.

---

### Example 1: Adding a file directly in `$HOME` (e.g. `~/.zshrc`)

1. **Create the file inside the home package**:
   ```bash
   mkdir -p ~/dotfiles/home
   ```

2. **Move your config into the package folder**:
   ```bash
   mv ~/.zshrc ~/dotfiles/home/.zshrc
   ```

3. **Symlink it with Stow**:
   ```bash
   cd ~/dotfiles
   stow home
   ```

---

### Example 2: Adding a folder in `~/.config/` (e.g. `~/.config/alacritty`)

1. **Create the directory inside the home package**:
   ```bash
   mkdir -p ~/dotfiles/home/.config
   ```

2. **Move your configuration folder into place**:
   ```bash
   mv ~/.config/alacritty ~/dotfiles/home/.config/
   ```

3. **Symlink it with Stow**:
   ```bash
   cd ~/dotfiles
   stow home
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
