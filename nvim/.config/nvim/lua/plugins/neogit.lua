return {
  {
    "NeogitOrg/neogit",
    dependencies = { "nvim-lua/plenary.nvim", "sindrets/diffview.nvim", "nvim-telescope/telescope.nvim" },
    cmd = "Neogit",
    keys = {
      { "<Leader>gg", "<Cmd>Neogit<CR>", desc = "Git status" },
      { "<Leader>gc", "<Cmd>Neogit commit<CR>", desc = "Git commit" },
    },
    opts = {
      integrations = { diffview = true, telescope = true },
    },
  },
}
