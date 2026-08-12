return {
  {
    "andythigpen/nvim-coverage",
    dependencies = { "nvim-lua/plenary.nvim" },
    cmd = {
      "Coverage",
      "CoverageLoad",
      "CoverageShow",
      "CoverageHide",
      "CoverageToggle",
      "CoverageClear",
      "CoverageSummary",
    },
    keys = {
      { "<leader>tc", "<cmd>CoverageToggle<cr>", desc = "Toggle coverage signs" },
      { "<leader>tl", "<cmd>CoverageLoad<cr>", desc = "Load coverage report" },
      { "<leader>ts", "<cmd>CoverageSummary<cr>", desc = "Coverage summary" },
      { "<leader>th", "<cmd>CoverageHide<cr>", desc = "Hide coverage signs" },
      { "<leader>tx", "<cmd>CoverageClear<cr>", desc = "Clear coverage data" },
    },
    config = function()
      require("coverage").setup {
        commands = true, -- create the :Coverage* user commands
        auto_reload = true, -- automatically reload the report when it changes
        highlights = {
          covered = { fg = "#C3E88D" },
          uncovered = { fg = "#F07178" },
        },
        signs = {
          covered = { hl = "CoverageCovered", text = "▎" },
          uncovered = { hl = "CoverageUncovered", text = "▎" },
        },
        summary = {
          min_coverage = 80.0, -- threshold used for highlighting in the summary popup
        },
        lang = {
          python = {
            coverage_file = ".coverage",
          },
        },
      }
    end,
  },
}

