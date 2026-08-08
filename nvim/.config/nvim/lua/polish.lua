-- This will run last in the AstroNvim setup process.

-- Automatically detect project .venv virtual environment and set PATH / VIRTUAL_ENV
-- This ensures Neovim debuggers (DAP), terminals, Pyright LSP, and runners use .venv/bin/python
vim.api.nvim_create_autocmd({ "VimEnter", "DirChanged" }, {
  desc = "Auto-detect project .venv virtual environment",
  callback = function()
    local cwd = vim.fn.getcwd()
    local venv_python = cwd .. "/.venv/bin/python"
    if vim.fn.executable(venv_python) == 1 then
      vim.env.VIRTUAL_ENV = cwd .. "/.venv"
      vim.env.PATH = cwd .. "/.venv/bin:" .. vim.env.PATH
    end
  end,
})
