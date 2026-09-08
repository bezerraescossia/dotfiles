-- Options are automatically loaded before lazy.nvim startup.
require("config.remote_clipboard").setup()
require("config.python_venv").activate()

vim.opt.relativenumber = false
vim.g.autoformat = false

-- Spellcheck both English and Portuguese (vim only ships a generic "pt"
-- spellfile, no pt_br variant; nvim downloads it on first use if missing).
vim.opt.spelllang = { "en", "pt" }
