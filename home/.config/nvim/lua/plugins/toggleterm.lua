---@type LazySpec
return {
  "akinsho/toggleterm.nvim",
  -- default direction for `:ToggleTerm`, `<F7>`, `<C-'>`, etc.
  opts = { direction = "float" },
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
