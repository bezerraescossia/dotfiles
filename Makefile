SHELL := /bin/sh

DOTFILES := $(CURDIR)
HOME_DIR ?= $(HOME)
STOW ?= stow
PACKAGES := nvim tmux wezterm
TPM_DIR ?= $(HOME_DIR)/.tmux/plugins/tpm

.PHONY: help install check-deps stow unstow restow install-tpm install-tmux-plugins

help:
	@printf '%s\n' \
		'Available targets:' \
		'  make install              Check dependencies, stow configs, and install TPM' \
		'  make check-deps           Check commands required by the configurations' \
		'  make stow                 Link Neovim, tmux, and WezTerm configs into $$HOME' \
		'  make unstow               Remove the links created by make stow' \
		'  make restow               Recreate all configuration links' \
		'  make install-tpm          Install the tmux plugin manager' \
		'  make install-tmux-plugins Install tmux plugins through TPM'

install: check-deps stow install-tpm
	@printf '%s\n' 'Setup complete. Start nvim or tmux to finish plugin initialization.'

check-deps:
	@missing=0; \
	for command in git $(STOW) nvim tmux rg tree-sitter lazygit gdu btm python3 uv node cc; do \
		if command -v "$$command" >/dev/null 2>&1; then \
			printf ' found %s\n' "$$command"; \
		else \
			printf ' missing %s\n' "$$command"; missing=1; \
		fi; \
		done; \
	if command -v fd >/dev/null 2>&1 || command -v fdfind >/dev/null 2>&1; then \
		printf '%s\n' ' found fd'; \
	else \
		printf '%s\n' ' missing fd (or fdfind)'; missing=1; \
	fi; \
	if command -v fc-match >/dev/null 2>&1 && fc-match 'Hack Nerd Font' | grep -qi 'Hack'; then \
		printf '%s\n' ' found Hack Nerd Font'; \
	else \
		printf '%s\n' ' missing Hack Nerd Font (required by wezterm/.wezterm.lua)'; missing=1; \
	fi; \
	clipboard=0; \
	for command in xclip xsel wl-copy pbcopy clip.exe; do \
		if command -v "$$command" >/dev/null 2>&1; then clipboard=1; break; fi; \
	done; \
	if [ "$$clipboard" -eq 1 ]; then \
		printf '%s\n' ' found clipboard tool'; \
	else \
		printf '%s\n' ' missing clipboard tool (install xclip, xsel, wl-clipboard, pbcopy, or clip.exe)'; missing=1; \
	fi; \
	if command -v wezterm >/dev/null 2>&1; then \
		printf '%s\n' ' found wezterm'; \
	else \
		printf '%s\n' ' warning: wezterm is not installed (install it for your OS/host)'; \
	fi; \
	if [ "$$missing" -ne 0 ]; then \
		printf '%s\n' 'Install the missing commands, then run make install again.' >&2; \
		exit 1; \
	fi

stow:
	$(STOW) --dir='$(DOTFILES)' --target='$(HOME_DIR)' $(PACKAGES)

unstow:
	$(STOW) --dir='$(DOTFILES)' --target='$(HOME_DIR)' --delete $(PACKAGES)

restow:
	$(STOW) --dir='$(DOTFILES)' --target='$(HOME_DIR)' --restow $(PACKAGES)

install-tpm:
	@if [ -d '$(TPM_DIR)/.git' ]; then \
		printf '%s\n' 'TPM already installed'; \
	else \
		printf '%s\n' 'Installing TPM'; \
		mkdir -p '$(TPM_DIR)'; \
		git clone --depth=1 https://github.com/tmux-plugins/tpm '$(TPM_DIR)'; \
	fi

install-tmux-plugins: install-tpm
	'$(TPM_DIR)/bin/install_plugins'
