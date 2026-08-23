-- Set by <leader>ts before triggering a load, so load_coverage_cb below
-- knows to pop the summary open once loading finishes. Left false for
-- plain CoverageLoad calls and auto_reload refreshes, so those stay silent.
local pending_summary = false

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
      { "<leader>to", "<cmd>CoverageLoad<cr>", desc = "Load coverage report" },
      {
        "<leader>ts",
        function()
          pending_summary = true
          require("coverage").load(false)
        end,
        desc = "Load coverage report and show summary",
      },
      { "<leader>th", "<cmd>CoverageHide<cr>", desc = "Hide coverage signs" },
      { "<leader>tx", "<cmd>CoverageClear<cr>", desc = "Clear coverage data" },
    },
    config = function()
      require("coverage").setup {
        commands = true, -- create the :Coverage* user commands
        auto_reload = true, -- automatically reload the report when it changes
        load_coverage_cb = function()
          if pending_summary then
            pending_summary = false
            require("coverage").summary()
          end
        end,
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
            coverage_command = "uv run coverage json --show-contexts -q -o -",
          },
        },
      }
    end,
  },
}

