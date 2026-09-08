-- Make pyright pick up the project's .venv/venv the moment it starts,
-- independent of autocmd ordering: lspconfig's `before_init` runs right
-- before the initialize request, with `config.root_dir` already resolved.
return {
  "neovim/nvim-lspconfig",
  opts = function(_, opts)
    opts.servers = opts.servers or {}
    opts.servers.pyright = opts.servers.pyright or {}
    local prev_before_init = opts.servers.pyright.before_init
    opts.servers.pyright.before_init = function(params, config)
      if prev_before_init then
        prev_before_init(params, config)
      end
      require("config.python_venv").activate(config.root_dir)
      if vim.env.VIRTUAL_ENV then
        config.settings = vim.tbl_deep_extend("force", config.settings or {}, {
          python = { pythonPath = vim.env.VIRTUAL_ENV .. "/bin/python" },
        })
      end
    end
  end,
}
