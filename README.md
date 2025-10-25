# Awesome [Zellij](https://github.com/zellij-org/zellij)

A list of resources for Zellij workspace: plugins, tutorials and configuration settings.

All the resources listed are community-driven: we cannot offer support but suggestions and comments are very welcome.

# Plugins

* [ghost](https://github.com/vdbulcke/ghost) spawn floating command terminal pane (interactive zrf)
* [gitpod.zellij](https://github.com/gitpod-samples/gitpod.zellij) Zellij plugin for Gitpod, with .gitpod.yml tasks integration
* [grab](https://github.com/imsnif/grab) A fuzzy finder (files, structs, enums, functions) for Rust devs
* [harpoon](https://github.com/Nacho114/harpoon) quickly navigate panes (clone of nvim's harpoon) 
* [jbz (Just Bacon Zellij)](https://github.com/nim65s/jbz) display your just commands wrapped in bacon
* [monocole](https://github.com/imsnif/monocle) fuzzy find of file names and contents
* [multitask](https://github.com/imsnif/multitask) a mini-CI as a Zellij plugin
* [room](https://github.com/rvcas/room) quickly search and switch tabs 🖤
* [vim-zellij-navigator](https://github.com/hiasr/vim-zellij-navigator) Seamless navigation with vim in zellij
* [zbuffers](https://github.com/Strech/zbuffers) a minimal and convenient way to switch between tabs, inspired by Emacs vertico-buffers and Zellij session-manager
* [zellij-autolock](https://github.com/fresh2dev/zellij-autolock) Automatically lock Zellij depending on the command in the focused pane. Seamless navigation for Vim and more. Pairs well with [zellij.vim](https://github.com/fresh2dev/zellij.vim). 
* [zellij-bookmarks](https://github.com/yaroslavborbat/zellij-bookmarks) manage command bookmarks and quickly insert them into the terminal
* [zellij-cb](https://github.com/ndavd/zellij-cb) a customizable compact bar for Zellij
* [zellij-choose-tree](https://github.com/laperlej/zellij-choose-tree) quickly switch between sessions, inspired by tmux choose-tree
* [zellij-datetime](https://github.com/h1romas4/zellij-datetime) adds a date and time pane to your Zellij
* [zellij-favs](https://github.com/JoseMM2002/zellij-favs) adds a way to save favorites sessions and flush the others
* [zellij-forgot](https://github.com/karimould/zellij-forgot) swiftly present and access your keybinds (and more)
* [zellij-getmode](https://github.com/chardskarth/zellij-getmode) a simple utility plugin that gets the current input mode of zellij
* [zellij-jump-list](https://github.com/blank2121/zellij-jump-list) navigate your motions from pane-to-pane (similar to Vim, Neovim, and Emacs jump list)
* [zellij-nvim-nav-plugin](https://github.com/sharph/zellij-nvim-nav-plugin) Another plugin for seamless navigation with neovim/vim windows
* [zellij-pane-picker](https://github.com/shihanng/zellij-pane-picker) quickly switch, star, and jump to panes with customizable keyboard shortcuts
* [zellij-playbooks](https://github.com/yaroslavborbat/zellij-playbooks) browse, select, and execute commands from playbook files directly in the terminal
* [zellij-sessionizer](https://github.com/laperlej/zellij-sessionizer) create sessions based on folder names
* [zellij-switch](https://github.com/mostafaqanbaryan/zellij-switch) switching between sessions in CLI using `zellij pipe`
* [zellij-what-time](https://github.com/pirafrank/zellij-what-time) shows host system date and/or time in the status bar. Inspired by zellij-datetime
* [zellij-workspace](https://github.com/vdbulcke/zellij-workspace) apply layouts to current session
* [zj-docker](https://github.com/dj95/zj-docker) display docker containers and perform basic operations
* [zj-status-bar](https://github.com/cristiand391/zj-status-bar) an opinionated fork of the compact-bar plugin
* [zj-quit](https://github.com/cristiand391/zj-quit) a friendly `quit` plugin for zellij 
* [zjpane](https://github.com/FuriouZz/zjpane) Navigate between zellij panes easily
* [zjstatus](https://github.com/dj95/zjstatus) a configurable, themeable statusbar plugin
* [zjstatus-hints](https://github.com/b0o/zjstatus-hints) adds mode-aware key binding hints to zjstatus
* [zjswitcher](https://github.com/WingsZeng/zjswitcher) automatically switch between normal mode and locked mode
* [zj-git-branch](https://github.com/dam4rus/zj-git-branch) Manage git branches
* [zsm](https://github.com/liam-mackie/zsm) A zoxide-integrated session switcher with support for default layouts

# Integrations

* [theylix](https://codeberg.org/hobgoblina/theylix) Zellij, Helix, and various cli tools ([Yazi](https://github.com/sxyazi/yazi), [Lazygit](https://github.com/jesseduffield/lazygit), [LazySQL](https://github.com/jorgerojas26/lazysql), [Slumber](https://github.com/LucasPickering/slumber), [Serpl](https://github.com/yassinebridi/serpl), `git blame` via [Tig](https://github.com/jonas/tig)) as a zen-mode IDE
* [yazelix](https://github.com/luccahuguet/yazelix) zellij, yazi and nushell adding a File Tree to Helix & helix-friendly keybindigs for zellij!
* [zeco](https://github.com/julianbuettner/zeco) Share your zellij session over the internet, easy and secure!
* [zellix](https://github.com/TheEmeraldBee/zellix) A nushell wrapper over helix that leverages the power of zellij to turn it into a plugin system!
* [zellij-sessionizer](https://github.com/victor-falcon/zellij-sessionizer) A fuzzy finder-powered project switcher for Zellij sessions, inspired by [ThePrimeagen/tmux-sessionizer](https://github.com/ThePrimeagen/tmux-sessionizer)
* [zide](https://github.com/josephschmitt/zide) Zellij layouts + bash scripts to create an IDE-like file picker and editor workflow that works in any shell and with most any visual file pickers!

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
