---@type LazySpec
return {
  {
    "mfussenegger/nvim-dap-python",
    ft = "python",
    dependencies = { "mfussenegger/nvim-dap" },
    config = function()
      -- use debugpy installed by Mason as the adapter; dap-python resolves the
      -- interpreter to debug (pythonPath) by looking for .venv/venv/env/.env
      -- next to the file, so per-project virtualenvs are picked up automatically
      require("dap-python").setup(vim.fn.stdpath "data" .. "/mason/packages/debugpy/venv/bin/python")
    end,
  },
  {
    -- disable mason-nvim-dap's default python handler: it inserts its own
    -- "Python: Launch file" config, which duplicates and is named
    -- inconsistently with the ones dap-python already provides above
    "jay-babu/mason-nvim-dap.nvim",
    opts = {
      handlers = {
        python = function() end,
      },
    },
  },
}
