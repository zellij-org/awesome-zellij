# Awesome [Zellij](https://github.com/zellij-org/zellij)

A list of resources for Zellij workspace: plugins, tutorials and configuration settings.

All the resources listed are community-driven: we cannot offer support but suggestions and comments are very welcome.

Last updated: 2026-03-04

## Maintainer flows

All project entries should be edited in `data/projects.json`.

Use one explicit flow when running the maintenance script:

```bash
# Full maintainer flow: refresh stars via GitHub API, then render README + timestamp.
# Token recommended to avoid API rate limits: set GITHUB_TOKEN or GH_TOKEN.
uv run scripts/update_readme_stars.py sync

# Maintainer/bot flow: refresh stars only (updates data/projects.json).
# Token recommended to avoid API rate limits: set GITHUB_TOKEN or GH_TOKEN.
uv run scripts/update_readme_stars.py refresh-stars

# Contributor-friendly flow: render README from data only (no API calls, no token needed).
uv run scripts/update_readme_stars.py render
```

Token setup (for `sync` / `refresh-stars`):

```bash
# temporary for current shell
export GITHUB_TOKEN=ghp_your_token_here

# or store in .env (script also accepts GH_TOKEN)
echo "GITHUB_TOKEN=ghp_your_token_here" >> .env
```

# Plugins

## Navigation

| Project | ⭐ | Description |
| --- | --- | --- |
| [harpoon](https://github.com/Nacho114/harpoon) | 179 | quickly navigate panes (clone of nvim's harpoon) |
| [room](https://github.com/rvcas/room) | 243 | quickly search and switch tabs 🖤 |
| [vim-zellij-navigator](https://github.com/hiasr/vim-zellij-navigator) | 158 | Seamless navigation with vim in zellij |
| [zellij-jump-list](https://github.com/blank2121/zellij-jump-list) | 23 | navigate your motions from pane-to-pane (similar to Vim, Neovim, and Emacs jump list) |
| [zellij-nvim-nav-plugin](https://github.com/sharph/zellij-nvim-nav-plugin) | 10 | Another plugin for seamless navigation with neovim/vim windows |
| [zellij-pane-picker](https://github.com/shihanng/zellij-pane-picker) | 16 | quickly switch, star, and jump to panes with customizable keyboard shortcuts |
| [zjpane](https://github.com/FuriouZz/zjpane) | 12 | Navigate between zellij panes easily |

## Session Management

| Project | ⭐ | Description |
| --- | --- | --- |
| [zbuffers](https://github.com/Strech/zbuffers) | 18 | a minimal and convenient way to switch between tabs, inspired by Emacs vertico-buffers and Zellij session-manager |
| [zellij-choose-tree](https://github.com/laperlej/zellij-choose-tree) | 39 | quickly switch between sessions, inspired by tmux choose-tree |
| [zellij-favs](https://github.com/JoseMM2002/zellij-favs) | 20 | adds a way to save favorites sessions and flush the others |
| [zellij-sessionizer](https://github.com/laperlej/zellij-sessionizer) | 69 | create sessions based on folder names |
| [zellij-switch](https://github.com/mostafaqanbaryan/zellij-switch) | 44 | switching between sessions in CLI using `zellij pipe` |
| [zsm](https://github.com/liam-mackie/zsm) | 29 | A zoxide-integrated session switcher with support for default layouts |

## Status Bar

| Project | ⭐ | Description |
| --- | --- | --- |
| [zellaude](https://github.com/ishefi/zellaude) | 7 | a status bar plugin that shows Claude Code activity indicators on tabs |
| [zellij-cb](https://github.com/ndavd/zellij-cb) | 38 | a customizable compact bar for Zellij |
| [zellij-datetime](https://github.com/h1romas4/zellij-datetime) | 47 | adds a date and time pane to your Zellij |
| [zellij-load](https://github.com/Christian-Prather/zellij-load) | 3 | show system resources such as CPU, memory and GPU usage |
| [zellij-what-time](https://github.com/pirafrank/zellij-what-time) | 13 | shows host system date and/or time in the status bar. Inspired by zellij-datetime |
| [zj-status-bar](https://github.com/cristiand391/zj-status-bar) | 35 | an opinionated fork of the compact-bar plugin |
| [zjstatus](https://github.com/dj95/zjstatus) | 875 | a configurable, themeable statusbar plugin |
| [zjstatus-hints](https://github.com/b0o/zjstatus-hints) | 53 | adds mode-aware key binding hints to zjstatus |

## UI & Modes

| Project | ⭐ | Description |
| --- | --- | --- |
| [zellij-autolock](https://github.com/fresh2dev/zellij-autolock) | 137 | Automatically lock Zellij depending on the command in the focused pane. Seamless navigation for Vim and more. Pairs well with [zellij.vim](https://github.com/fresh2dev/zellij.vim). |
| [zellij-forgot](https://github.com/karimould/zellij-forgot) | 218 | swiftly present and access your keybinds (and more) |
| [zellij-getmode](https://github.com/chardskarth/zellij-getmode) | 0 | a simple utility plugin that gets the current input mode of zellij |
| [zellij-layoutswitch](https://github.com/sgtrusty/zellij-layoutswitch) | 1 | switch between layouts and tab panes natively & efficiently without shell bloat |
| [zellij-newtab-plus](https://github.com/AlexZasorin/zellij-newtab-plus) | 8 | create named tabs and navigate using zoxide in one keybind |
| [zellij-tab-bar-indexed](https://github.com/ivoronin/zellij-tab-bar-indexed) | 9 | a tab-bar plugin that adds numeric indices to tabs for quick navigation |
| [zellij-vertical-tabs](https://github.com/cfal/zellij-vertical-tabs) | 17 | a plugin that displays tabs vertically as rows |
| [zellij-workspace](https://github.com/vdbulcke/zellij-workspace) | 33 | apply layouts to current session |
| [zjswitcher](https://github.com/WingsZeng/zjswitcher) | 13 | automatically switch between normal mode and locked mode |

## Search

| Project | ⭐ | Description |
| --- | --- | --- |
| [grab](https://github.com/imsnif/grab) | 20 | A fuzzy finder (files, structs, enums, functions) for Rust devs |
| [monocle](https://github.com/imsnif/monocle) | 185 | fuzzy find of file names and contents |

## Utilities

| Project | ⭐ | Description |
| --- | --- | --- |
| [ghost](https://github.com/vdbulcke/ghost) | 58 | spawn floating command terminal pane (interactive zrf) |
| [multitask](https://github.com/imsnif/multitask) | 139 | a mini-CI as a Zellij plugin |
| [zellij-attention](https://github.com/KiryuuLight/zellij-attention) | 3 | add notification icons to tab names when panes need attention, designed for Claude Code |
| [zellij-bookmarks](https://github.com/yaroslavborbat/zellij-bookmarks) | 35 | manage command bookmarks and quickly insert them into the terminal |
| [zellij-notepad](https://github.com/0xble/zellij-notepad) | 4 | floating notepad pane with configurable editor, position, and timestamped notes |
| [zellij-playbooks](https://github.com/yaroslavborbat/zellij-playbooks) | 16 | browse, select, and execute commands from playbook files directly in the terminal |
| [zellij-qr-share](https://github.com/dbachelder/zellij-qr-share) | 5 | show a web token as a QR code in the terminal for fast mobile authentication in the web UI |
| [zellij-send-keys](https://github.com/atani/zellij-send-keys) | 10 | send text/commands to specific panes like tmux send-keys |
| [zj-quit](https://github.com/cristiand391/zj-quit) | 43 | a friendly `quit` plugin for zellij |

## External Tools

| Project | ⭐ | Description |
| --- | --- | --- |
| [gitpod.zellij](https://github.com/gitpod-samples/gitpod.zellij) | 9 | Zellij plugin for Gitpod, with .gitpod.yml tasks integration |
| [jbz (Just Bacon Zellij)](https://github.com/nim65s/jbz) | 42 | display your just commands wrapped in bacon |
| [zellijira](https://github.com/dam4rus/zellijira) | 2 | Manage sessions around on Jira issues |
| [zj-docker](https://github.com/dj95/zj-docker) | 39 | display docker containers and perform basic operations |
| [zj-git-branch](https://github.com/dam4rus/zj-git-branch) | 5 | Manage git branches |

# Integrations

| Project | ⭐ | Description |
| --- | --- | --- |
| [fzf-zellij](https://github.com/k-kuroguro/fzf-zellij) | 11 | Shell script to start fzf in a Zellij floating pane. |
| [opencode-zellij-namer](https://github.com/24601/opencode-zellij-namer) | 28 | AI-powered dynamic session naming for [OpenCode](https://opencode.ai), automatically renames sessions based on project context |
| [theylix](https://codeberg.org/hobgoblina/theylix) | 1 | Zellij, Helix, and various cli tools ([Yazi](https://github.com/sxyazi/yazi), [Lazygit](https://github.com/jesseduffield/lazygit), [LazySQL](https://github.com/jorgerojas26/lazysql), [Slumber](https://github.com/LucasPickering/slumber), [Serpl](https://github.com/yassinebridi/serpl), `git blame` via [Tig](https://github.com/jonas/tig)) as a zen-mode IDE |
| [yazelix](https://github.com/luccahuguet/yazelix) | 818 | zellij, yazi and nushell adding a File Tree to Helix & helix-friendly keybindigs for zellij! |
| [zeco](https://github.com/julianbuettner/zeco) | 60 | Share your zellij session over the internet, easy and secure! |
| [zellij-sessionizer](https://github.com/victor-falcon/zellij-sessionizer) | 40 | A fuzzy finder-powered project switcher for Zellij sessions, inspired by [ThePrimeagen/tmux-sessionizer](https://github.com/ThePrimeagen/tmux-sessionizer) |
| [zellix](https://github.com/TheEmeraldBee/zellix) | 50 | A nushell wrapper over helix that leverages the power of zellij to turn it into a plugin system! |
| [zide](https://github.com/josephschmitt/zide) | 288 | Zellij layouts + bash scripts to create an IDE-like file picker and editor workflow that works in any shell and with most any visual file pickers! |
| [zrw](https://github.com/ivoronin/zrw) | 4 | run commands in Zellij panes, wait for completion, and propagate exit codes |

# Tutorials

## Basics

* [Zellij basic functionality](https://zellij.dev/tutorials/basic-functionality/)
* [Using and creating Layouts](https://zellij.dev/tutorials/layouts/)

## Plugins

* [A comprehensive walkthrough on developing Zellij plugins](https://github.com/Kangaxx-0/first-zellij-plugin)
* [Learnings from developing a zellij plugin](https://blog.nerd.rocks/posts/profiling-zellij-plugins/) an informative blog post from the creator of [zjstatus](https://github.com/dj95/zjstatus)
* [Developing WebAssembly Rust plugins for Zellij](https://www.youtube.com/watch?v=pgNIcQ8rTXk) Aram Drevekenin's talk at RustLab 2023
* [How to use Zellij Switch plugin](https://mostafaqanbaryan.com/zellij-attach-plugin/) a blog post about using fzf and zoxide with zellij-switch

## Documentation and support

* [The zellij docs](https://zellij.dev/documentation/introduction)
* and of course the zellij [Discord](https://discord.com/invite/CrUAFH3) and [Matrix](https://matrix.to/#/#zellij_general:matrix.org) for questions, support and discussions
