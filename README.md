# Dotfiles

My personal configuration files, managed with [GNU Stow](https://www.gnu.org/software/stow/). This setup is designed primarily for **macOS** (with support for **Linux**) and features a modern terminal workflow centered around Neovim, Tmux, and Zsh/Fish.

## 📂 Structure

The repository is organized by topic (application). GNU Stow symlinks these directories to your home directory (`~`).

```text
├── aerospace/      # Tiling window manager (macOS)
├── fish/           # Fish shell configuration
├── lazygit/        # Git TUI configuration
├── linearmouse/    # Mouse customization (macOS)
├── nvim/           # Neovim (Kickstart-based)
├── sketchybar/     # Status bar (macOS)
├── starship/       # Cross-shell prompt
├── tmux/           # Terminal multiplexer
├── yazi/           # Terminal file manager
├── zed/            # Zed editor configuration
└── zsh/            # Zsh shell configuration
```

## 🛠️ Prerequisites

Before installing, ensure you have the following essential tools and fonts:

### 1. Nerd Font (Required)
A **[Nerd Font](https://www.nerdfonts.com/font-downloads)** is required for icons in Neovim, Tmux, Starship, and Sketchybar to render correctly.
*   *Recommendation:* **JetBrainsMono Nerd Font** or **Hack Nerd Font**.

### 2. Package Manager
*   **macOS:** [Homebrew](https://brew.sh/) is required.
    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```
*   **Linux:** `apt` (Debian/Ubuntu) or your distro's package manager.

### 3. Core Dependencies
Install these tools using your package manager before bootstrapping:

**macOS (Homebrew):**
```bash
brew install stow git neovim tmux zsh fish yazi starship lazygit ripgrep fd fzf bat zoxide nvm uv
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt update
sudo apt install stow git neovim tmux zsh fish ripgrep fd-find fzf bat
# Note: You may need to install 'yazi', 'starship', 'zoxide', etc. manually or via their install scripts on Linux.
```

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/dotfiles.git ~/dotfiles
cd ~/dotfiles
```

### 2. Prepare for Zsh (Important)
If you plan to use Zsh, install **[Oh My Zsh](https://ohmyz.sh/)** *before* running the bootstrap script.
```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```
**⚠️ Note:** Oh My Zsh will create a default `.zshrc` file. You **must delete it** so that `stow` can link the one from this repo without conflict.
```bash
rm ~/.zshrc
```

### 3. Run the bootstrap script
This script will symlink the configuration files to your home directory.
```bash
./bootstrap.sh
```

## ⚡ Post-Installation Steps

After running the bootstrap script, perform these final setup steps:

### Neovim
Open Neovim. The package manager (`lazy.nvim`) will automatically bootstrap and install all plugins.
```bash
nvim
```

### Tmux
Launch Tmux. The configuration checks for the **Tmux Plugin Manager (TPM)** and should install it automatically.
```bash
tmux
```
*   If plugins don't load immediately, press `Prefix` + `I` (default prefix is `Ctrl+s`) to install them.

### Shells (Zsh / Fish)
*   **Zsh:** If you haven't already, ensure Oh My Zsh is installed. The `.zshrc` expects plugins like `fzf-tab`, `zsh-autosuggestions`, and `zsh-syntax-highlighting`. You may need to install these plugins into `~/.oh-my-zsh/custom/plugins/`.
*   **Set Default Shell:**
    ```bash
    chsh -s $(which zsh)  # or $(which fish)
    ```

### macOS Specifics
*   **Aerospace:** You may need to restart the application or log out/in for the window manager to take effect. Grant necessary Accessibility permissions in System Settings.
*   **Sketchybar:** Ensure you have the necessary helper tools installed (like `lua` or specific fonts if the default configuration requires them).

## 🗑️ Uninstallation

To remove the symlinks (and restore your previous config if you backed it up):

```bash
cd ~/dotfiles
stow -D -t ~ nvim tmux zsh ... # list the packages you want to unstow
```
