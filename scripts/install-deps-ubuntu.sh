#!/usr/bin/env bash
# Installs the tools required by `make check-deps` / `make check-deps-nvim`
# on Ubuntu or Debian (apt-based). Idempotent: skips anything already installed.
set -euo pipefail

if [ "$(id -u)" -eq 0 ]; then
	SUDO=""
else
	SUDO="sudo"
fi

DISTRO_ID=$(. /etc/os-release && echo "$ID")

case "$(uname -m)" in
	x86_64) ARCH=amd64 ;;
	aarch64|arm64) ARCH=arm64 ;;
	*) echo "Unsupported architecture: $(uname -m)" >&2; exit 1 ;;
esac

have() { command -v "$1" >/dev/null 2>&1; }

NVIM_MIN_VERSION=0.11.0
nvim_version_ok() {
	have nvim || return 1
	v=$(nvim --version | head -1 | awk '{print $2}' | tr -d v)
	[ "$(printf '%s\n%s\n' "$v" "$NVIM_MIN_VERSION" | sort -V | tail -1)" = "$v" ]
}

echo "==> apt packages"
$SUDO apt update
$SUDO apt install -y git stow tmux ripgrep fd-find xclip build-essential python3 python3-pip unzip curl gpg fontconfig

echo "==> fd (symlink fdfind -> fd)"
mkdir -p "$HOME/.local/bin"
if ! have fd; then
	ln -sf "$(command -v fdfind)" "$HOME/.local/bin/fd"
fi
case ":$PATH:" in
	*":$HOME/.local/bin:"*) ;;
	*) echo "note: add \$HOME/.local/bin to your PATH to use fd, uv, etc." ;;
esac

echo "==> neovim (>= ${NVIM_MIN_VERSION}, required by AstroNvim)"
if ! nvim_version_ok; then
	# Debian/Ubuntu apt packages lag well behind upstream (e.g. trixie ships 0.10.4),
	# so install the official prebuilt release instead of relying on apt.
	nvim_arch=$([ "$ARCH" = amd64 ] && echo x86_64 || echo arm64)
	curl -Lo /tmp/nvim.tar.gz "https://github.com/neovim/neovim/releases/latest/download/nvim-linux-${nvim_arch}.tar.gz"
	$SUDO rm -rf "/opt/nvim-linux-${nvim_arch}"
	$SUDO tar -C /opt -xzf /tmp/nvim.tar.gz
	$SUDO ln -sf "/opt/nvim-linux-${nvim_arch}/bin/nvim" /usr/local/bin/nvim
fi

echo "==> node.js"
if ! have node; then
	if [ "$DISTRO_ID" = "ubuntu" ]; then
		# Ubuntu's apt nodejs can be quite old; NodeSource tracks current LTS releases
		# and bundles npm into the nodejs package.
		curl -fsSL https://deb.nodesource.com/setup_lts.x | $SUDO -E bash -
		$SUDO apt install -y nodejs
	else
		# Debian splits npm into its own package.
		$SUDO apt install -y nodejs npm
	fi
fi

echo "==> uv"
if ! have uv; then
	curl -LsSf https://astral.sh/uv/install.sh | sh
fi

echo "==> tree-sitter CLI"
if ! have tree-sitter; then
	$SUDO npm install -g tree-sitter-cli
fi

echo "==> lazygit"
if ! have lazygit; then
	lg_arch=$([ "$ARCH" = amd64 ] && echo x86_64 || echo arm64)
	lg_version=$(curl -s "https://api.github.com/repos/jesseduffield/lazygit/releases/latest" | grep -Po '"tag_name": "v\K[^"]*')
	curl -Lo /tmp/lazygit.tar.gz "https://github.com/jesseduffield/lazygit/releases/latest/download/lazygit_${lg_version}_Linux_${lg_arch}.tar.gz"
	tar -xf /tmp/lazygit.tar.gz -C /tmp lazygit
	$SUDO install /tmp/lazygit /usr/local/bin
fi

echo "==> gdu"
if ! have gdu; then
	$SUDO apt install -y gdu || {
		curl -Lo /tmp/gdu.tgz "https://github.com/dundee/gdu/releases/latest/download/gdu_linux_${ARCH}.tgz"
		tar -xf /tmp/gdu.tgz -C /tmp
		$SUDO install "/tmp/gdu_linux_${ARCH}" /usr/local/bin/gdu
	}
fi

echo "==> bottom (btm)"
if ! have btm; then
	# The .deb filename includes a package-revision suffix (e.g. "-1") that
	# doesn't match the release tag, so pull the exact asset URL from the release JSON.
	btm_url=$(curl -s "https://api.github.com/repos/ClementTsang/bottom/releases/latest" \
		| grep -Po '"browser_download_url": "\Khttps://[^"]*_'"${ARCH}"'\.deb' \
		| grep -v musl | head -1)
	curl -Lo /tmp/bottom.deb "$btm_url"
	$SUDO dpkg -i /tmp/bottom.deb
fi

echo "==> wezterm (official apt repo)"
if ! have wezterm; then
	$SUDO mkdir -p /etc/apt/keyrings
	curl -fsSL https://apt.fury.io/wez/gpg.key | $SUDO gpg --yes --dearmor -o /etc/apt/keyrings/wezterm-fury.gpg
	echo 'deb [signed-by=/etc/apt/keyrings/wezterm-fury.gpg] https://apt.fury.io/wez/ * *' | $SUDO tee /etc/apt/sources.list.d/wezterm-fury.list >/dev/null
	$SUDO apt update
	$SUDO apt install -y wezterm
fi

echo "==> Hack Nerd Font"
if ! (have fc-match && fc-match 'Hack Nerd Font' | grep -qi 'Hack'); then
	mkdir -p "$HOME/.local/share/fonts"
	curl -Lo /tmp/Hack.zip https://github.com/ryanoasis/nerd-fonts/releases/latest/download/Hack.zip
	unzip -o /tmp/Hack.zip -d "$HOME/.local/share/fonts" >/dev/null
	fc-cache -f "$HOME/.local/share/fonts"
fi

echo "==> done. Run 'make check-deps' (or 'make check-deps-nvim') to verify."
