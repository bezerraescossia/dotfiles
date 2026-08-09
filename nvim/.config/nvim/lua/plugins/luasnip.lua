-- lua/plugins/luasnip.lua
return {
  "L3MON4D3/LuaSnip",
  version = "v2.*",
  build = "make install_jsregexp",
  config = function()
    local ls = require("luasnip")

    -- 1. Keymaps para navegar nos choices
    vim.keymap.set({ "i", "s" }, "<C-j>", function()
      if ls.choice_active() then
        ls.change_choice(1)
      end
    end, { silent = true, desc = "Cycle next choice" })

    vim.keymap.set({ "i", "s" }, "<C-k>", function()
      if ls.choice_active() then
        ls.change_choice(-1)
      end
    end, { silent = true, desc = "Cycle previous choice" })

    vim.keymap.set("i", "<C-e>", function()
      if ls.choice_active() then
        require("luasnip.extras.select_choice")()
      end
    end, { desc = "Select LuaSnip choice from menu" })

    -- 2. Carrega automaticamente todos os snippets da pasta lua/snippets/
    require("luasnip.loaders.from_lua").lazy_load({
      paths = vim.fn.stdpath("config") .. "/lua/snippets",
    })
  end,
}
