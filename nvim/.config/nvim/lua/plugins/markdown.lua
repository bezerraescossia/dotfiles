return {
  -- Markdown is rendered in the browser, not in the buffer.
  { "MeanderingProgrammer/render-markdown.nvim", enabled = false },

  {
    "iamcco/markdown-preview.nvim",
    cmd = { "MarkdownPreview", "MarkdownPreviewStop", "MarkdownPreviewToggle" },
    ft = { "markdown" },
    -- mkdp#util#install lives in the plugin's autoload dir, so the plugin has
    -- to be on the rtp before the build step can call it.
    build = function()
      vim.cmd([[Lazy load markdown-preview.nvim]])
      vim.fn["mkdp#util#install"]()
    end,
    init = function()
      -- Keep the tab open when leaving the buffer, and follow the cursor.
      vim.g.mkdp_auto_close = 0
      vim.g.mkdp_preview_options = { disable_sync_scroll = 0 }
    end,
    keys = {
      {
        "<leader>cp",
        ft = "markdown",
        "<cmd>MarkdownPreviewToggle<cr>",
        desc = "Markdown Preview",
      },
    },
  },
}
