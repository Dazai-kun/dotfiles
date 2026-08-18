# Repository Guidelines

## Project Structure & Module Organization

This is a GNU Stow-managed dotfiles repository. Each top-level directory is a Stow package whose contents mirror paths under `$HOME`: for example, `nvim/.config/nvim/` maps to `~/.config/nvim/`, while `zsh/.zshrc` maps to `~/.zshrc`. Core cross-platform packages include `fish`, `nvim`, `tmux`, `zsh`, `yazi`, `starship`, `lazygit`, and `zed`. macOS-specific configuration lives in `aerospace`, `linearmouse`, and `sketchybar`. `bootstrap.sh` installs links for the supported platform; `README.md` documents prerequisites and setup.

Keep application-specific files inside their existing package. Neovim extensions belong under `nvim/.config/nvim/lua/custom/plugins/`; Sketchybar helpers belong under `sketchybar/.config/sketchybar/plugins/`.

## Build, Test, and Development Commands

There is no compilation step or repository-wide test suite. Use focused validation:

- `./bootstrap.sh` installs all applicable packages into `$HOME`. It changes live symlinks, so review changes first.
- `stow --simulate --verbose --target="$HOME" nvim` previews one package without modifying links.
- `stow --restow --target="$HOME" nvim` refreshes links after a package changes.
- `nvim --headless '+checkhealth' +qa` runs Neovim health checks.
- `bash -n bootstrap.sh` checks bootstrap script syntax.

Replace `nvim` in Stow commands with the package being developed.

## Coding Style & Naming Conventions

Preserve the conventions of each tool and avoid unrelated reformatting. Shell scripts use Bash, two-space indentation, quoted variables, and fail-fast behavior (`set -e`). Lua uses two spaces and the repository's `nvim/.config/nvim/.stylua.toml`; run `stylua nvim/.config/nvim` when available. Keep TOML, YAML, and JSON valid and follow nearby key ordering. Use lowercase, descriptive filenames; Neovim plugin modules use names such as `render-markdown.lua`.

## Testing Guidelines

Validate only the packages you changed. Run syntax or parser checks where supported, preview Stow operations, then launch the affected application and confirm that configuration loads without errors. For UI changes, verify keybindings, icons, and platform-specific behavior manually. Document manual checks in the pull request.

## Commit & Pull Request Guidelines

History uses short, imperative subjects, with occasional Conventional Commit prefixes such as `feat:`. Prefer focused messages like `feat: add Neovim image rendering` or `fix: correct Sketchybar battery state`. Pull requests should explain the affected packages, motivation, validation performed, and macOS/Linux impact. Include screenshots for visible editor, bar, or window-manager changes, and call out new external dependencies or required permissions.

## Security & Configuration

Do not commit secrets, tokens, machine-specific credentials, or generated caches. Keep reusable defaults in the repository and load sensitive values from environment variables or untracked local files.
