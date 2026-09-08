-- Autocmds are automatically loaded on the VeryLazy event
-- Default autocmds that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/autocmds.lua
--
-- Add any additional autocmds here
-- with `vim.api.nvim_create_autocmd`
--
-- Or remove existing autocmds by their group name (which is prefixed with `lazyvim_` for the defaults)
-- e.g. vim.api.nvim_del_augroup_by_name("lazyvim_wrap_spell")

-- Exempt *word*/**word** from spellcheck inside comments and docstrings
-- (markdown files are handled separately, via a treesitter query override).
require("config.nospell_docstring").setup()

-- Re-detect the venv relative to the buffer's own directory, in case nvim
-- was started outside the project (e.g. `nvim ai-services/src/foo.py` from
-- its parent dir), where the cwd-based detection in options.lua misses it.
vim.api.nvim_create_autocmd("FileType", {
  pattern = "python",
  group = vim.api.nvim_create_augroup("python_venv_autodetect", { clear = true }),
  callback = function(ev)
    require("config.python_venv").activate(vim.fs.dirname(vim.api.nvim_buf_get_name(ev.buf)))
  end,
})

-- <F4> runs the current file with plain `python3` in a Snacks terminal
-- split, for when you just want to see stdout without attaching the
-- debugger (already on <F5> via nvim-dap). `python3` resolves through
-- $PATH, which python_venv_autodetect above keeps pointed at the active
-- venv, so this picks up the same interpreter dap-python would use.
vim.api.nvim_create_autocmd("FileType", {
  pattern = "python",
  group = vim.api.nvim_create_augroup("python_run_file", { clear = true }),
  callback = function(ev)
    vim.keymap.set("n", "<F4>", function()
      vim.cmd("silent! update")
      Snacks.terminal({ "python3", vim.api.nvim_buf_get_name(ev.buf) }, {
        win = { position = "bottom" },
        interactive = false,
      })
    end, { buffer = ev.buf, desc = "Run: Python file (no debug)" })
  end,
})

-- nvim-dap-python only registers "file" / "file:args" / "attach" /
-- "file:doctest" in the DAP config picker. Add a "pytest" entry alongside
-- them to run the current file under pytest instead of `python`.
-- pythonPath is left unset so dap-python's own enrich_config resolves it
-- from $VIRTUAL_ENV, same as its built-in configs.
vim.api.nvim_create_autocmd("FileType", {
  pattern = "python",
  group = vim.api.nvim_create_augroup("dap_python_pytest_config", { clear = true }),
  callback = function()
    local ok, dap = pcall(require, "dap")
    if not ok then
      return
    end
    local configs = dap.configurations.python or {}
    dap.configurations.python = configs
    for _, config in ipairs(configs) do
      if config.name == "pytest" then
        return
      end
    end
    table.insert(configs, {
      type = "python",
      request = "launch",
      name = "pytest",
      module = "pytest",
      args = { "-s", "${file}" },
      console = "integratedTerminal",
    })
  end,
})
