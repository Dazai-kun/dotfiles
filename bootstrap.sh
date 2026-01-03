#!/usr/bin/env bash
set -e

DOTFILES_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DOTFILES_DIR"

echo "Bootstrapping dotfiles from $DOTFILES_DIR"

# Ensure XDG config directory exists
mkdir -p "$HOME/.config"

# Ensure GNU Stow is installed
if ! command -v stow >/dev/null 2>&1; then
  echo "GNU Stow not found. Installing..."

  if [[ "$OSTYPE" == "darwin"* ]]; then
    if ! command -v brew >/dev/null 2>&1; then
      echo "Homebrew is required but not installed."
      exit 1
    fi
    brew install stow
  else
    sudo apt update
    sudo apt install -y stow
  fi
fi

# Core, cross-platform packages
stow -t "$HOME" \
  fish \
  nvim \
  tmux \
  zsh \
  yazi \
  starship \
  lazygit \
  zed

# macOS-only packages
if [[ "$OSTYPE" == "darwin"* ]]; then
  stow -t "$HOME" \
    sketchybar \
    aerospace \
    linearmouse
fi

if [ ! -d "$HOME/.oh-my-zsh" ]; then
    echo "⚠️  Note: Oh My Zsh is not detected at ~/.oh-my-zsh."
    echo "   Your .zshrc expects it. Install it via: https://ohmyz.sh"
fi

echo "Dotfiles installed successfully."
