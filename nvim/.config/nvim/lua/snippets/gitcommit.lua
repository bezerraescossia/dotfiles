-- lua/snippets/all.lua
local ls = require("luasnip")
local s = ls.snippet
local c = ls.choice_node
local t = ls.text_node
local i = ls.insert_node

return {
  s("cmsg", {
    c(1, {
      t("feat"),
      t("fix"),
      t("docs"),
      t("style"),
      t("refactor"),
      t("perf"),
      t("test"),
      t("build"),
      t("ci"),
      t("chore"),
      t("revert"),
    }),
    t("("),
    i(2, "scope"),
    t("): "),
    i(3, "description"),
  }),
}
