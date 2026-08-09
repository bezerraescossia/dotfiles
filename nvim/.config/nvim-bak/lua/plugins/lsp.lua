return {
  {
    "williamboman/mason.nvim",
    opts = {},
  },
  {
    "williamboman/mason-lspconfig.nvim",
    opts = {
      -- Ensures pyright is automatically installed by Mason
      ensure_installed = { "pyright" },
    },
  },
  {
    "neovim/nvim-lspconfig",
    dependencies = {
      "williamboman/mason.nvim",
      "williamboman/mason-lspconfig.nvim",
      "hrsh7th/cmp-nvim-lsp", -- Optional: connects LSP capabilities to nvim-cmp
    },
    config = function()
      local lspconfig = require("lspconfig")

      -- Integrate LSP with nvim-cmp autocompletion if present
      local capabilities = vim.lsp.protocol.make_client_capabilities()
      local ok_cmp, cmp_nvim_lsp = pcall(require, "cmp_nvim_lsp")
      if ok_cmp then
        capabilities = cmp_nvim_lsp.default_capabilities()
      end

      -- Disable dynamic file watching to avoid tmux buffer overflows / crashes
      capabilities.workspace = capabilities.workspace or {}
      capabilities.workspace.didChangeWatchedFiles = {
        dynamicRegistration = false,
      }

      -- Configure Pyright
      lspconfig.pyright.setup({
        capabilities = capabilities,
        settings = {
          pyright = {
            -- Using Ruff or Black for formatting instead of Pyright
            disableOrganizeImports = false,
          },
          python = {
            analysis = {
              autoSearchPaths = true,
              typeCheckingMode = "basic", -- Options: "off", "basic", "strict"
              useLibraryCodeForTypes = true,
            },
          },
        },
      })

      -- Keymaps for LSP actions when an LSP attaches to a buffer
      vim.api.nvim_create_autocmd("LspAttach", {
        group = vim.api.nvim_create_augroup("UserLspConfig", {}),
        callback = function(ev)
          local opts = { buffer = ev.buf }
          vim.keymap.set("n", "gd", vim.lsp.buf.definition, opts)
          vim.keymap.set("n", "K", vim.lsp.buf.hover, opts)
          vim.keymap.set("n", "<leader>rn", vim.lsp.buf.rename, opts)
          vim.keymap.set({ "n", "v" }, "<leader>ca", vim.lsp.buf.code_action, opts)
        end,
      })
    end,
  },
}
