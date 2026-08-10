return {
  "L3MON4D3/LuaSnip",
  config = function(plugin, opts)
    -- Run default AstroNvim setup
    require("astronvim.plugins.configs.luasnip")(plugin, opts)

    -- Load loose VSCode-style *.code-snippets files (no package.json manifest
    -- required, unlike from_vscode.lazy_load/load).
    local from_vscode = require("luasnip.loaders.from_vscode")
    local snippet_dirs = {
      vim.fn.expand "~/.config/Code/User/snippets",
      vim.fn.getcwd() .. "/.vscode",
    }
    for _, dir in ipairs(snippet_dirs) do
      for _, file in ipairs(vim.fn.glob(dir .. "/*.code-snippets", true, true)) do
        from_vscode.load_standalone { path = file }
      end
    end

    local ls = require("luasnip")
    local s = ls.snippet
    local t = ls.text_node
    local i = ls.insert_node
    local c = ls.choice_node

    -- Add snippet to gitcommit filetype
    ls.add_snippets("gitcommit", {
      s("cc", {
        -- 1. Choice node for Conventional Commit types
        c(1, {
          t("feat"),
          t("fix"),
          t("docs"),
          t("style"),
          t("refactor"),
          t("perf"),
          t("test"),
          t("chore"),
          t("build"),
          t("ci"),
        }),
        -- 2. Optional scope
        t("("), i(2, "scope"), t("): "),
        -- 3. Commit message summary
        i(3, "description"),
        -- 4. Optional body / breaking changes breaking point
        t({ "", "", "" }),
        i(0),
      }),
    })
  end,
}

