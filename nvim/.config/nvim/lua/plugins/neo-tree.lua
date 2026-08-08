---@type LazySpec
return {
  "nvim-neo-tree/neo-tree.nvim",
  opts = {
    filesystem = {
      filtered_items = {
        visible = false,         -- Do not force-render filtered items
        hide_dotfiles = false,   -- Show dotfiles (.env, .python-version, etc.)
        hide_gitignored = false, -- Show gitignored files (.venv, etc.)
        hide_by_name = {
          "__pycache__",
          ".pytest_cache",
          ".ruff_cache",
          ".mypy_cache",
          ".DS_Store",
        },
        hide_by_pattern = {
          "*.pyc",
          "*.pyo",
          "*.pyd",
        },
        never_show = {
          "__pycache__",
          ".pytest_cache",
          ".ruff_cache",
          ".mypy_cache",
        },
        never_show_by_pattern = {
          "*.pyc",
          "*.pyo",
          "*.pyd",
        },
      },
    },
  },
}
