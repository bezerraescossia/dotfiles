-- Auto-detect a project-local Python virtualenv (.venv or venv) and export
-- it via $VIRTUAL_ENV / $PATH, the way `source .venv/bin/activate` would.
-- Since pyright, nvim-dap-python and :terminal all inherit the editor's
-- environment, one activation covers LSP, debugging and the terminal.
local M = {}

-- The "<dir>/bin:" prefix this module itself last prepended to PATH, if
-- any. Tracked (rather than a one-time snapshot of the original PATH) so
-- that plugins which mutate PATH after this module loads — notably
-- mason.nvim, which runs later during lazy.nvim startup and prepends its
-- own bin dir — don't get silently undone the next time a venv activates.
local injected_prefix = nil

local function find_venv(start)
  -- Force absolute: `start` can still be a relative buffer path this early
  -- in a FileType autocmd (e.g. a buffer opened via a relative CLI arg),
  -- and vim.fs.find's upward search then returns a relative result too —
  -- which downstream consumers like dap-python's $VIRTUAL_ENV resolution
  -- treat as relative to *their* process cwd, not the project root.
  start = vim.fn.fnamemodify(start, ":p")
  local dir = vim.fs.find({ ".venv", "venv" }, { path = start, upward = true, type = "directory" })[1]
  if not dir then
    return nil
  end
  local python = dir .. "/bin/python"
  if vim.uv.fs_stat(python) then
    return dir, python
  end
end

-- Activate the venv found by walking up from `start` (defaults to cwd).
-- No-op if no venv is found or it's already active.
function M.activate(start)
  local venv_dir, python = find_venv(start or vim.loop.cwd())
  if not venv_dir or vim.env.VIRTUAL_ENV == venv_dir then
    return
  end
  if injected_prefix and vim.env.PATH:sub(1, #injected_prefix) == injected_prefix then
    vim.env.PATH = vim.env.PATH:sub(#injected_prefix + 1)
  end
  local prefix = venv_dir .. "/bin:"
  vim.env.VIRTUAL_ENV = venv_dir
  vim.env.PATH = prefix .. vim.env.PATH
  injected_prefix = prefix
  vim.g.python3_host_prog = python
end

return M
