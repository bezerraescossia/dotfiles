local function find_venv_activate()
  local start = vim.api.nvim_buf_get_name(0)
  start = start ~= "" and vim.fs.dirname(start) or vim.fn.getcwd()
  local venv = vim.fs.find(".venv", { path = start, upward = true, type = "directory" })[1]
  if not venv then return nil end
  local activate = venv .. "/bin/activate"
  return vim.fn.filereadable(activate) == 1 and activate or nil
end

---@type LazySpec
return {
  "akinsho/toggleterm.nvim",
  -- default direction for `:ToggleTerm`, `<F7>`, `<C-'>`, etc.
  opts = {
    direction = "float",
    on_open = function(term)
      if term.venv_activated then return end
      local activate = find_venv_activate()
      if not activate then return end
      term.venv_activated = true
      -- give the shell a moment to reach its prompt before sending input
      vim.defer_fn(function() term:send("source " .. vim.fn.shellescape(activate), false) end, 100)
    end,
  },
  specs = {
    {
      "AstroNvim/astrocore",
      opts = function(_, opts)
        local astro = require "astrocore"
        local python = vim.fn.executable "python3" == 1 and "python3" or vim.fn.executable "python" == 1 and "python"
        if python then
          opts.mappings.n["<F4>"] = {
            function()
              vim.cmd "silent! update"
              astro.toggle_term_cmd {
                cmd = python .. " " .. vim.fn.shellescape(vim.fn.expand "%:p"),
                direction = "float",
                -- keep the terminal open so output/tracebacks stay readable
                -- after a quick script finishes instead of flashing closed
                close_on_exit = false,
              }
            end,
            desc = "Run Python file",
          }
        end
      end,
    },
  },
}
