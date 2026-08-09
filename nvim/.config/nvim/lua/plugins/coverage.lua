return {
  "andythigpen/nvim-coverage",
  dependencies = { "nvim-lua/plenary.nvim" },
  config = function()
    require("coverage").setup {
      auto_reload = true,
      commands = true, -- creates :Coverage, :CoverageLoad, :CoverageToggle, etc.
      highlights = {
        -- Customize line indicator colors
        covered = { fg = "#C3E88D" }, -- Soft green for covered lines
        uncovered = { fg = "#F07178" }, -- Soft red for uncovered lines
      },
      signs = {
        covered = { hl = "CoverageCovered", text = "▎" },
        uncovered = { hl = "CoverageUncovered", text = "▎" },
      },
      summary = {
        -- Options for the summary window popup
        min_coverage = 80.0,
      },
    }
  end,
}
