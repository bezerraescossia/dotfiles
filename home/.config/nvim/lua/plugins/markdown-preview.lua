-- Live markdown preview in the browser, with built-in Mermaid diagram support
-- `:MarkdownPreview` / `<Leader>mp` opens a synced preview tab; `:MarkdownPreviewStop` closes it

---@type LazySpec
return {
  "iamcco/markdown-preview.nvim",
  cmd = { "MarkdownPreviewToggle", "MarkdownPreview", "MarkdownPreviewStop" },
  ft = { "markdown" },
  build = function() vim.fn["mkdp#util#install"]() end,
  init = function()
    vim.g.mkdp_filetypes = { "markdown" }
    vim.g.mkdp_theme = "dark"
  end,
  specs = {
    {
      "AstroNvim/astrocore",
      opts = {
        mappings = {
          n = {
            ["<Leader>mp"] = { "<cmd>MarkdownPreviewToggle<cr>", desc = "Markdown Preview" },
          },
        },
      },
    },
  },
}
